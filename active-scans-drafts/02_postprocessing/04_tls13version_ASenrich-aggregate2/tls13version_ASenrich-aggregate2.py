import argparse
import os
import threading
import subprocess
import sys
import re
import orjson
import select
from pathlib import Path
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from functools import lru_cache
import gc

LOOKUP_PY = "./lookup.py"

parser = argparse.ArgumentParser()
parser.add_argument('--basedir', help='base dir to search files within')
args = parser.parse_args()

if not args.basedir:
  print("--basedir needs to be supplied")
  exit(0)

baseDir = args.basedir
lockDir = './lock_bookkeeping/'

@lru_cache(maxsize=1000)
def get_fd_for_file(path):
  return path.open('ab')

def processFile(p, doneName, workName):
  print("Processing", p)
  Path(workName).touch()

  path = str(p).split('/')
  struct = path[len(path)-5:][:5]
  postfix = '/'.join(struct[3:])[:-8] + '_' + struct[2] + '.json' # remove .json.gz and append _list
  prefix = struct[1]

  p_lookup = subprocess.Popen(['python3', LOOKUP_PY], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  p_jq = subprocess.Popen(['jq', '-c', '.+(if ."tls-full" then ."tls-full" else ."tls-SH"end|{ip,timestamp})'], stdin=subprocess.PIPE, stdout=p_lookup.stdin)
  p_gzip = subprocess.Popen(['gzip', '-d', '-c', str(p)], stdout=p_jq.stdin)

  # ommiting the go part here, this is simply spreading out to news .json files
  
  print("Waiting for input")
  linecount = 0
  while True:
    timeout = 5
    ret_gzip = p_gzip.poll()
    (readable, _, _) = select.select([p_lookup.stdout], [], [], timeout) # close if nothing came anymore for 5secs
    if len(readable) == 0:
      if ret_gzip == None:
        sys.stderr.write("WARNING: No input for {} seconds, but {} is still running\n".format(timeout, 'gzip'))
        continue
      else:
        break
    linecount += 1
    if linecount%100 == 0:
      print('.', end='')
      sys.stdout.flush()
    if linecount%10000 == 0:
      gc.collect() # lru cache safety net
      if linecount%100000 == 0:
        print("\tLine {}".format(linecount))
    l =  p_lookup.stdout.readline()
    js = orjson.loads(l)
    if 'asn' in js:
      outf = Path('{}/as_{}/{}'.format(prefix, js['asn'], postfix))
      outf.parent.mkdir(parents=True, exist_ok=True) # touch dir

      get_fd_for_file(outf).write(l)
      # with outf.open('ab') as af:
      #   af.write(l)

  # gzip jq and lookup should have ended by now
  print("Done", p)
  ret_gzip = p_gzip.wait()
  if ret_gzip:
    raise NameError("gzip error: {}".format(ret_gzip))

  # TODO lookup does not terminate on closed stdin
  p_lookup.stdin.close()
  # ret_lookup = p_lookup.wait()
  # if ret_lookup:
  #   raise NameError("{} error: {}".format(LOOKUP_PY, ret_lookup))
  ret_lookup = p_lookup.poll()
  if ret_lookup != None:
    # should still be running due to open p_lookup.stdin
    # if it terminated already, there was probably a broken pipe which was ignored by the script
    raise NameError("{} error (if 0, pipe broke): {}".format(LOOKUP_PY, ret_lookup))

  print("Waiting for jq")
  p_jq.stdin.close()
  ret_jq = p_jq.wait()
  if ret_jq:
    raise NameError("jq error: {}".format(ret_jq))

  print("Waiting for lookup")
  ret_lookup = p_lookup.wait()
  if ret_lookup:
    raise NameError("{} error: {}".format(LOOKUP_PY, ret_lookup))

  if (ret_gzip == 0) and (ret_jq == 0):
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
