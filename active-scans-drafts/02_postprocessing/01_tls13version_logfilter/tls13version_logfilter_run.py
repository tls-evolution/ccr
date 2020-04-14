import argparse
import os
import threading
import subprocess
import sys
from pathlib import Path
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor

parser = argparse.ArgumentParser()
parser.add_argument('--basedir', required=True, help='base dir to search files within')
parser.add_argument('--buckets', required=True, type=int, help='Number of files to which domains are distributed. WARNING: MUST be the same for all logs of a domain-list! Hints: {com-list: 50, alexa: 0}')
args = parser.parse_args()

baseDir = args.basedir
lockDir = './lock/'


MAXP = 10
POOL = ThreadPoolExecutor(MAXP)
LOCK = threading.Lock()
WRITERS = {}


def getWriter(tid):
  global LOCK, WRITERS
  with LOCK:
    writer = WRITERS.get(tid)
    if writer:
      return writer
    cmd = ['./tls13version_logfilter', '--tls-eval']
    if int(args.buckets) > 0:
      cmd.append('--buckets={}'.format(int(args.buckets)))
    writer = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=sys.stderr)
    WRITERS[tid] = writer
    return writer
    

def processFile(p, doneName, workName):
  print("Processing", p)
  Path(workName).touch()
  writer = getWriter(threading.current_thread().ident)
  p0 = subprocess.Popen(['brotli', '-d', '-c', str(p)], stdout=writer.stdin, stderr=sys.stderr)
  exitcode = p0.wait()
  if exitcode == 0:
    size = Path(p).stat().st_size
    with open(doneName,"w") as f:
      f.write(str(size))
    if os.path.isfile(workName):
      os.remove(workName)
  else:
    print("Brotli exited with", exitcode)
  return exitcode == 0

def deleteFiles(l):
  for f in l:
    os.remove(str(f))

def processPath(p):
  if p.is_dir():
    dirs = [x for x in p.iterdir()]
    dirs.sort()
    for d in dirs:
      processPath(d)
  else:
    if str(p)[-len(".json.br"):] != ".json.br":
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
    todel = Path('/'.join(struct[:2])).rglob(files) # this is lazy

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
      deleteFiles(todel)
      os.remove(workName)

    #work = POOL.submit(processFile, p, doneName, workName)
    processFile(p, doneName, workName)
 


processPath(Path(baseDir))
#processFile(baseDir + '/2018/02/tls-version-grabber-all-recent_alexa-A-www_2018-02-27.json.br', 'test.done', 'test.work')

