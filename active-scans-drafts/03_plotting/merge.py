import json
import itertools
from pathlib import Path
import argparse
from collections import OrderedDict

def merge_d(old, new):
  for k,v in new.items():
    if k in old:
      # merge
      if type(v) is OrderedDict:
        merge_d(old[k], new[k])
      else:
        old[k] += new[k]
    else:
      # simply take the new value
      old[k] = new[k]
  
def merge(dirS, outDir):
  # step1: find all years/months for each dir in dirS
  files = [[x.stem for x in Path(d).glob('*.json')] for d in dirS]
  merged = sorted(set(itertools.chain(*files)))
  for date in merged:
    mdata = OrderedDict()
    for d in dirS:
      p = Path('{}/{}.json'.format(d, date))
      if not p.exists():
        continue
      with p.open('r') as json_file:
        merge_d(mdata, json.load(json_file, object_pairs_hook=OrderedDict))
    p = Path('{}/{}.json'.format(outDir, date))
    p.parent.mkdir(parents=True, exist_ok=True) # touch dir
    with p.open('w') as json_file:
      json.dump(mdata, json_file)

parser = argparse.ArgumentParser()
parser.add_argument('--in', action='append', dest='input',required=True)
parser.add_argument('--out', required=True)
parser.add_argument('--prefix', default='')
args = parser.parse_args()

if (not args.input) or (len(args.input) < 2) :
  print("Need to specify at least two --in <directories>")
  exit(-1)

inputs = [args.prefix + i for i in args.input]
output = args.prefix + args.out

if Path(output).exists():
  print("Output ({}) already exists, aborting".format(output))
  exit(-1)

merge(inputs, output)
