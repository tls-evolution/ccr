import argparse
import os
import threading
import subprocess
import sys
import re
from pathlib import Path
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--basedir', help='base dir to search files within')
args = parser.parse_args()

if not args.basedir:
  print("--basedir needs to be supplied")
  exit(0)

baseDir = args.basedir
lockDir = './lock_bookkeeping/'

MAXP = 4
POOL = ThreadPoolExecutor(MAXP)
LOCK = threading.Lock()
WRITERS = {}
PART_REX = re.compile('.*_part(....)\.json.gz')

def getWriter(key, prefix, part):
  global LOCK, WRITERS
  with LOCK:
    key_full = key
    if part:
        key_full += "_part" + part
    writer = WRITERS.get(key_full)
    print("writer_key: ", key_full)
    if writer:
      return writer
    if part:
      writer = subprocess.Popen(['./tls13version_aggregate1', '-prefix', prefix, '-part', '_part' + part], stdin=subprocess.PIPE, stderr=sys.stderr)
    else:
      writer = subprocess.Popen(['./tls13version_aggregate1', '-prefix', prefix], stdin=subprocess.PIPE, stderr=sys.stderr)
    WRITERS[key_full] = writer
    return writer    

def processFile(writer, p, doneName, workName):
  print("Processing", p)

  Path(workName).touch()
  p0 = subprocess.Popen(['gzip', '-d', '-c', str(p)], stdout=writer.stdin, stderr=sys.stderr)
  exitcode = p0.wait()
  if exitcode == 0:
    size = Path(p).stat().st_size
    with open(doneName,"w") as f:
      f.write(str(size))
    if os.path.isfile(workName):
      os.remove(workName)
  else:
    print("gzip exited with", exitcode)
    raise NameError("gzip exited: {}".format(exitcode))
  return exitcode == 0

def deleteFiles(l):
  for f in l:
    os.remove(str(f))

def sort_by_parts(x):
  global PART_REX
  part = PART_REX.fullmatch(x.name)
  if part:
    pt = part.group(1)
    return pt + x.name
  return x.name

WORKGROUP = defaultdict(list)

def processGroup(k, g):
  (key, prefix, part) = k
  print("Prefix is", prefix, "Part is", part, "Key is", key)

  writer = getWriter(key, prefix, part)

  for i in g:
    processFile(writer, i['file'], i['doneName'], i['workName'])

  print("Flushing", k)
  writer.stdin.write(b'END\n')
  writer.stdin.flush()
  ret_writer = writer.wait()
  if ret_writer != 0:
      raise NameError("tls13version_aggregate1 returned {}".format(ret_writer))

def processPath(p):
  global PART_REX, POOL, WORKGROUP
  if p.is_dir():
    dirs = [x for x in p.iterdir()]
    dirs.sort(key=lambda x: sort_by_parts(x))
    for d in dirs:
      processPath(d)
  else:
    if str(p)[-len(".json.gz"):] != ".json.gz":
        print("Skipping", p)
        return
    if Path(p).stat().st_size == 0:
        print ("WARNING: Skipping empty file", p)
        return
    path = str(p).split('/')

    struct = path[len(path)-5:][:5]
    lockBase = lockDir + '/'.join(struct)
    workName = lockBase + '.work'
    doneName = lockBase + '.done'
    basedir = os.path.dirname(lockBase)

    key = '/'.join(struct[:4]) # everything up to filename == unique key
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
        raise NameError("Cleanup needed before redoing {}".format(p))
        return
    elif os.path.isfile(workName):
      print("Redoing (unfinished)", p)
      raise NameError("Cleanup needed before redoing {}".format(p))
      os.remove(workName)

    prefix = './' + '/'.join(struct[:2])
    part = PART_REX.fullmatch(p.name)
    if part:
      part = part.group(1)

    # each group may only be processed by the same thread => build workgroups
    WORKGROUP[(key, prefix, part)].append({'file': p, 'doneName': doneName, 'workName': workName})
 


processPath(Path(baseDir))
if len(WORKGROUP) > 0:
  keys = [k for k in WORKGROUP.keys()]
  keys.sort()
  for k in keys:
    processGroup(k, WORKGROUP[k])
    #POOL.submit(processGroup, k, v)

