#!/bin/bash

python3 merge.py --prefix=data/ --out _com-net-org --in com-A-www --in net-A-www --in org-A-www

python3 merge.py --prefix=data/ --out _all-but-com-net-org $(ls data/ | grep -v -e '^_' -e "^toplistsAlexaUmbrellaMajestic-A-www$" -e "^alexa-A-www$" -e "^majestic-A-www$" -e "^umbrella-A-www$" -e "^alexa-A-www_domainsNotInZoneLists$" -e "^majestic-A-www_domainsNotInZoneLists$" -e "^umbrella-A-www_domainsNotInZoneLists$" -e "^com-A-www$" -e "^net-A-www$" -e "^org-A-www$" | xargs printf -- '--in %s\n' | xargs)

python3 merge.py --prefix=data/ --out _all $(ls data/ | grep -v -e '^_' -e "^toplistsAlexaUmbrellaMajestic-A-www$" -e "^alexa-A-www$" -e "^majestic-A-www$" -e "^umbrella-A-www$" -e "^alexa-A-www_domainsNotInZoneLists$" -e "^majestic-A-www_domainsNotInZoneLists$" -e "^umbrella-A-www_domainsNotInZoneLists$" | xargs printf -- '--in %s\n' | xargs)
