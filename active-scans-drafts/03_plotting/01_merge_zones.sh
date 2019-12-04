#!/bin/bash

python3 zone_merge.py --prefix=data/ --out _com-net-org --in com-A-www --in net-A-www --in org-A-www

python3 zone_merge.py --prefix=data/ --out _all-but-com-net-org $(ls data/ | grep -v -e '^_' -e "^alexa-A-www" -e "^com-A-www" -e "^net-A-www" -e "^org-A-www" | xargs printf -- '--in %s\n' | xargs)

python3 zone_merge.py --prefix=data/ --out _all $(ls data/ | grep -v -e '^_' | xargs printf -- '--in %s\n' | xargs)

