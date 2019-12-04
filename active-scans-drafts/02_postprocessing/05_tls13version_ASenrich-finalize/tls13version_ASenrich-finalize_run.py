import argparse
import os
import threading
import subprocess
import shutil
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

MAXP = 4
POOL = ThreadPoolExecutor(MAXP)
LOCK = threading.Lock()
WRITERS = {}
PART_REX = re.compile('.*_part(....)\.json.gz')
ZONEPART_REX = re.compile('(..)_.*\.json')
WORKGROUP = defaultdict(list)

def deleteFiles(l):
  for f in l:
    os.remove(str(f))

def processPath(p):
  global WORKGROUP
  if p.is_dir():
    dirs = [x for x in p.iterdir()]
    dirs.sort()
    for d in dirs:
      processPath(d)
  else:
    path = str(p).split('/')

    struct = path[len(path)-5:][:5]
    prefix = './' + '/'.join(struct[1:4])
    month = p.name[:2]

    key = prefix + '_' + month
    WORKGROUP[key].append(p)

# Collect all work
processPath(Path(baseDir))

# Process work (could parallelize over WORKGROUP's)
keys = [k for k in WORKGROUP.keys()]
keys.sort()
for k in keys:
  v = WORKGROUP[k]
  print("Started group", k)
  if os.path.exists(k + ".json"):
      print("\tSkipping: outputfile already exists")
      continue
  writer = subprocess.Popen(['./tls13version_ASenrich-finalize', '-prefix', k], stdin=subprocess.PIPE)
  for p in v:
    if p.suffix == '.gz':
      print("Processing wth gzip", p)
      p0 = subprocess.Popen(['gzip', '-d', '-c', str(p)], stdout=writer.stdin)
      exitcode = p0.wait()
      if exitcode != 0:
        raise NameError("gzip returned {}".format(ret_writer))
    elif p.suffix == '.json':
      print("Copying raw json", p)
      with p.open("rb") as f:
        shutil.copyfileobj(f, writer.stdin)

  print("Flushing", k)
  writer.stdin.write(b'END\n')
  writer.stdin.flush()
  ret_writer = writer.wait()
  if ret_writer != 0:
    raise NameError("tls13version_aggregate2 returned {}".format(ret_writer))

