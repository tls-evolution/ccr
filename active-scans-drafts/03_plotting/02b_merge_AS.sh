#!/bin/bash

source ./config_AS.sh

# Merge results of different AS numbers into one
python3 merge.py --prefix=data_AS/ --out _AMAZON $(for AS in $AMAZON; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _GOOGLE $(for AS in $GOOGLE; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _CLOUDFLARE $(for AS in $CLOUDFLARE; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _AKAMAI $(for AS in $AKAMAI; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _MICROSOFT $(for AS in $MICROSOFT; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _FACEBOOK $(for AS in $FACEBOOK; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _DIGITALOCEAN $(for AS in $DIGITALOCEAN; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _OVH $(for AS in $OVH; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _GODADDY $(for AS in $GODADDY; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _SQUARESPACE $(for AS in $SQUARESPACE; do echo -n " --in as_${AS}"; done; echo "")
python3 merge.py --prefix=data_AS/ --out _SINGLEHOP $(for AS in $SINGLEHOP; do echo -n " --in as_${AS}"; done; echo "")

