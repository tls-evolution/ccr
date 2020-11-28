import argparse
import os
import threading
import subprocess
import sys
import re
import orjson
import select
import shutil
from pathlib import Path
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from functools import lru_cache
from fnvhash import fnv1a_32
import gc

parser = argparse.ArgumentParser()
parser.add_argument('--basedir', help='base dir to search files within')


args = parser.parse_args()

if not args.basedir:
  print("--basedir needs to be supplied")
  exit(0)

baseDir = args.basedir
lockDir = './lock_bookkeeping/'

DOM_REX = re.compile('domain":"(.*?)"')


def processStash(stash, inputFile, prefix, postfix):
  path = str(inputFile).split('/')
  outPath = path.copy()
  orig = path[-1]
  month = orig[:2]
  glob = month + '_part*.json.gz'
  path = path[:-1]

  outPath[-3] = outPath[-3] + '_domainsNotInZoneLists'

  outf = Path('/'.join(outPath[len(outPath)-4:][:4]))
  outf.parent.mkdir(parents=True, exist_ok=True)
  p_gzip_outfile = subprocess.Popen(['gzip'], stdin=subprocess.PIPE, stdout=outf.open('wb'))

  def writeEntry(entry):
    p_gzip_outfile.stdin.write(entry)
    # p_gzip_outfile.stdin.write(b'\n')
    pass

  print("Processing toplist stash now")
  for zone in stash:
    zonedir = path
    zonedir[-2] = zone
    pp = Path('/'.join(path))
    parts = list(pp.glob(glob))
    print("Processing zone {} ({} domains)".format(zone, len(stash[zone])))
    zonefiles = []
    if len(parts) > 0:
      for part in sorted(parts):
        zonefiles.append(part)
    else:
      zonefile = pp.joinpath(orig)
      if zonefile.exists():
        zonefiles.append(zonefile)
      else:
        print("WARNING: Zone scan not available: {}".format(zonefile));
    
    for zonefile in zonefiles:
      print("Checking {} domains of {} in toplist against {}".format(len(stash[zone]), zone, zonefile))

      p_gzip_zonefile = subprocess.Popen(['gzip', '-d', '-c', zonefile], stdout=subprocess.PIPE)
      linecount = 0
      for line in p_gzip_zonefile.stdout:
        linecount += 1
        # if linecount % 100000:
        #   print(".", end='', flush=True)
        
        match = DOM_REX.search(line.decode('utf-8'))
        if not match:
          raise NameError("could not find domain name in line: {}".format(line))
        domain = match[1]
        
        # remove the domain from the toplist results if it's included
        removed = stash[zone].pop(domain, None)
        # if removed:
        #   print("Removed {}".format(domain))

      ret_gzip_zonefile = p_gzip_zonefile.wait()
      if ret_gzip_zonefile:
        raise NameError("gzip error: {}, {}".format(zonefile, ret_gzip_zonefile))

    print("{} domains of {} not in zonefile: Writing them".format(len(stash[zone]), zone))
    domaincount = 0
    for domain in stash[zone]:
      domaincount += 1
      # if domaincount % 100000:
      #   print(".", end='', flush=True)
      writeEntry(stash[zone][domain])

    print("")


  p_gzip_outfile.stdin.close()
  ret_gzip_outfile = p_gzip_outfile.wait()
  if ret_gzip_outfile:
    raise NameError("gzip error: {}, {}".format("outfile", ret_gzip_outfile))

  print("DONE")

def processFile(p, doneName, workName):
  print("Processing", p)
  Path(workName).touch()

  path = str(p).split('/')
  struct = path[len(path)-5:][:5]
  postfix = '/'.join(struct[3:])[:-8] + '_' + struct[2] + '.json' # remove .json.gz and append _list
  prefix = struct[1]

  toplistStash = {}
  p_gzip = subprocess.Popen(['gzip', '-d', '-c', str(p)], stdout=subprocess.PIPE)

  # ommiting the go part here, this is simply spreading out to news .json files
  
  print("Waiting for input")
  linecount = 0
  for line in p_gzip.stdout:
    match = DOM_REX.search(line.decode('utf-8'))
    if not match:
      raise NameError("could not find domain name in line: {}".format(line))
    domain = match[1]
    domain_parts = domain.split('.')
    tld = domain_parts[-1]
    domain_lead = domain_parts[0]
    zone = '{}-A-{}'.format(tld, domain_lead)
    if len(domain_parts) != 3:
      # includes a subdomain (www.*.domain.tld)
      pass # do not skip subdomains
    toplistStash.setdefault(zone, {})
    toplistStash[zone][domain] = line

  ret_gzip = p_gzip.wait()
  if ret_gzip:
    raise NameError("gzip error: {}".format(ret_gzip))

  if (ret_gzip == 0):
    processStash(toplistStash, p, prefix, postfix)
    size = Path(p).stat().st_size
    with open(doneName,"w") as f:
      f.write(str(size))
    if os.path.isfile(workName):
      os.remove(workName)

def deleteFiles(l):
  for f in l:
    #print("\t\t deleting {}".format(str(f)))
    os.remove(str(f))

def processPath(p):
  if p.is_dir():
    dirs = [x for x in p.iterdir()]
    dirs.sort()
    for d in dirs:
      processPath(d)
  else:
    if str(p)[-len(".json.gz"):] != ".json.gz":
        print("Skipping", p)
        return
    path = str(p).split('/')

    struct = path[len(path)-5:][:5]
    lockBase = lockDir + '/'.join(struct)
    workName = lockBase + '.work'
    doneName = lockBase + '.done'
    basedir = os.path.dirname(lockBase)

    date = str(p).split(".json", 1)[0][-10:]
    files = ('{}_{}_*orig{}.json.gz'.format(struct[0], struct[1], date))

    struct_month_and_ending = struct[-1]
    struct_month = struct_month_and_ending[:2]
    struct_year = struct[-2]
    struct_list = struct[-3]
    struct_scanner = struct[-4]

    if not os.path.exists(basedir):
      os.makedirs(basedir)

    if os.path.isfile(doneName):
      if os.path.isfile(workName): # clean leftover .work
        os.remove(workName)
      want = size = Path(p).stat().st_size
      with open(doneName,"r") as f:
        haveS = f.readline().strip()
        try:
          have = int(haveS)
          if have == want:
            print("\tSkipping", p)
            return # we can skip this one
        except:
          pass
        # gotta redo this file
        print("Need to redo (size change)", p)
        return
        #deleteFiles(todel)
        #os.remove(doneName)
    elif os.path.isfile(workName):
      print("Redoing (unfinished)", p)
      # todel = Path('{}'.format(struct_scanner)).glob("*/{}/{}*_{}.*".format(struct_year, struct_month, struct_list))

      print("\tDeleting files", end='')
      if "_part" in path:
          raise NotImplementedError("Only supporting deletion for full month, not for parts of it")
      raise NotImplementedError("Code not written for this special script; I think it would NOT delete the special but the original files which we MUST keep!")
      sys.stdout.flush()
      dirs = Path('{}'.format(struct_scanner)).glob("*/{}".format(struct_year))
      dircount = 0
      for directory in dirs:
        dircount += 1
        if (dircount % 100) == 0:
          print('.', end = '')
          sys.stdout.flush()
        todel = directory.glob("{}*_{}.*".format(struct_month, struct_list))
        try:
          deleteFiles(todel)
        except Exception as e:
          print("Error while processing {}".format(directory))
          raise e
      print("\tdone deleting.")
      os.remove(workName)

    #work = POOL.submit(processFile, p, doneName, workName)
    processFile(p, doneName, workName)
 


processPath(Path(baseDir))

#processFile(Path('/opt/jost/aggregated/tls-version-grabber-all-recent/bank-A-www/2018/03.json.gz'), 'unused', 'unused')

#processFile(Path('/opt/jost/filtered/tls-version-grabber-all-recent/ch-A-www/2018/03/tls-version-grabber-all-recent_ch-A-www_2018-03-01_orig2018-03-01.json.gz'))
