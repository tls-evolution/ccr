import logging
import argparse
import pyasn
import sys
import errno
import json
import os
import subprocess
from datetime import datetime
from ftplib import FTP
from pathlib import Path

dict2list = lambda dic: [(k, v) for (k, v) in dic.items()]
list2dict = lambda lis: dict(lis)

logger = logging.getLogger( __name__ )
logger.setLevel( 'DEBUG' )
logger.addHandler( logging.StreamHandler( sys.stderr ) )

#asndb = pyasn.pyasn('ipasn_20180109.1200.gz')
#asndb = pyasn.pyasn('ipasn_20190318.0800.gz')

#2019-05-23

RIBS_PATH = './RIBS/'

CACHE = {}
BLACKLIST = set(['ipasn_20180618.0000.bz2'])

def getDatabase(year, month, day):
  key = (year, month, day)
  if key in CACHE:
    return CACHE[key]

  prefix = 'rib.{0}{1:02}{2:02}.'.format(year, month, day)
  fname = 'rib.{0}{1:02}{2:02}.0000.bz2'.format(year, month, day)
  ifname = 'ipasn_{0}{1:02}{2:02}.0000'.format(year, month, day)
  igfname = 'ipasn_{0}{1:02}{2:02}.0000.gz'.format(year, month, day)
  pfname = Path(RIBS_PATH + fname)
  ipfname = Path(RIBS_PATH + ifname)
  igpfname = Path(RIBS_PATH + igfname)

  if not igpfname.exists():
    logger.info('Downloading ' + fname)
    ftp = FTP('archive.routeviews.org')
    ftp.login()
    ftp.cwd('bgpdata/{0}.{1:02}/RIBS'.format(year, month))
    files = sorted([x for x in ftp.nlst() if (not (x in BLACKLIST)) and x.startswith(prefix)])
    fixedfname = next(x for x in files if ftp.size(x) > 100*1024*1024)
    logger.info("real name: " + fixedfname)

    pfname.parent.mkdir(parents=True, exist_ok=True)
    pfname.touch(exist_ok=True)
    handle = pfname.open('wb')
    ftp.retrbinary('RETR ' + fixedfname, handle.write)
    handle.close()
    ftp.quit()

    subprocess.run(['pyasn_util_convert.py', '--single', pfname.as_posix(), ipfname.as_posix()])
    pfname.unlink() # delete the .rib
    subprocess.run(['gzip', '--best', ipfname.as_posix()])

  logger.info("loading " + igpfname.as_posix())
  db = pyasn.pyasn(igpfname.as_posix())
  CACHE[key] = db
  return db
  

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def lookup(dic, key, *keys):
  if dic == None:
    return None
  if keys:
    return lookup(dic.get(key, {}), *keys)
  return dic.get(key)

try:
  for line in sys.stdin:
    try:
      js = json.loads(line)
    except:
      sys.stderr.write("WARNING\t json.loads failed: ", line)
      continue #ignore malformed input

    ip = js.get('ip')
    ts = [int(x) for x in (js.get('timestamp').split('T')[0]).split('-')]
    asndb = getDatabase(ts[0], ts[1], ts[2])
    (asn, _) = asndb.lookup(ip)
    if asn:
      js["asn"] = asn

    sys.stdout.write(json.dumps(js)+'\n')
except IOError as e:
  if e.errno == errno.EPIPE:
    pass
