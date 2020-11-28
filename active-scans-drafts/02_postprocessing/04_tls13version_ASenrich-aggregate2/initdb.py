import subprocess
import sys
import datetime

LOOKUP_PY = "./lookup.py"

START = datetime.date(2017, 10, 01)
END = datetime.date(2019, 11, 01)
for d in (START + datetime.timedelta(n) for n in range((END-START).days)):
  print("Fetching ASN db for", d)
  p0 = subprocess.Popen(['python3', LOOKUP_PY], stdin=subprocess.PIPE, stdout=sys.stdin)
  s = '{"ip":"127.0.0.1", "timestamp":"' + str(d) + '"}'
  p0.stdin.write(bytes(s, 'utf-8'))
  p0.stdin.close()
  p0.wait()
