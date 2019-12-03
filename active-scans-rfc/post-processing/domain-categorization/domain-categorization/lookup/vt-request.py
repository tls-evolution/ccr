import csv
import os
import re
import requests
import sys
import time

if len(sys.argv) != 3:
    print("Usage: python3 {} INPUT_FILE WORKDIR".format(sys.argv[0]))
    sys.exit(-1)

r = re.compile(".*goscanner.hosts.")

INPUT_FILE = os.path.basename(sys.argv[1])
INPUT_FILE_SPLIT = INPUT_FILE.split("_")
EPOCH = INPUT_FILE_SPLIT[0]
LIST_TYPE = INPUT_FILE_SPLIT[1]
BASENAME = r.search(INPUT_FILE).group()
SAMPLE_TYPE, SAMPLE_SIZE = INPUT_FILE.split(BASENAME)[1].rstrip(".csv").split(".")
WORKDIR=sys.argv[2]
URL = 'https://www.virustotal.com/vtapi/v2/domain/report'
MAX_RETRIES = 20

apikey = ""

with open("apikey", "r") as infh:
    line = infh.read()
    apikey = line.strip()    

p = os.path.join(WORKDIR, EPOCH, LIST_TYPE)
os.makedirs(p)
OUTPUT_FILE = os.path.join(p, "mapping.csv") 

to_try = []
retry_counter = 0
backoff = 1

def save_remainder(n):
    with open(BASENAME + SAMPLE_TYPE + "." + str(n) + "-" + SAMPLE_SIZE + ".csv", "w") as outfh:
        csv_writer = csv.writer(outfh)
        for i in to_try[n:]:
            csv_writer.writerow([i])

with open(INPUT_FILE, "r") as infh, open(OUTPUT_FILE, "w") as outfh:
    csv_reader = csv.reader(infh, delimiter=',')
    csv_writer = csv.writer(outfh, delimiter=',')
    for row in csv_reader:
        to_try.append(row)

    index = 0
    while index < len(to_try):
        row = to_try[index]
        index += 1
        if len(row) > 1:
            domain = row[1]
        else:
            domain = row[0]
        
        params = {'apikey': apikey,'domain': domain}
        try:
            response = requests.get(URL, params=params)
        except Exception as e:
            print("Exception for domain {}".format(domain))
            print("Exception is {}".format(e))
            if retry_counter == MAX_RETRIES:
                print("Maximum number of retries reached; aborting.")
                save_remainder(i + 1)
                sys.exit(-1)
            else:
                print("Connection exception. Appending {} to domains to query.".format(domain))
                to_try.append(row)
                retry_counter += 1
                time.sleep(backoff * 60)
                if backoff < 30:
                    backoff *= 4
                else:
                    backoff = 30
                continue


        if response.status_code != 200:
            if retry_counter == MAX_RETRIES:
                print("We received a status code {} for {}. MAX_RETRIES reached. Stopping.".format(response.status_code, domain))
                save_remainder(i + 1)
                sys.exit(-1)
            else:
                print("Non-HTTP 200. Appending {} to domains to query.".format(domain))
                to_try.append(row)
                retry_counter += 1
                time.sleep(backoff * 60)
                if backoff < 30:
                    backoff *= 4
                else:
                    backoff = 30
                continue

        try:
            j = response.json()
        except Exception as e:
            if retry_counter == MAX_RETRIES:
                print("We have a JSON decoding error for {}. MAX_RETRIES reached. Stopping.".format(domain))
                save_remainder(i + 1)
                sys.exit(-1)
            else:
                print("JSON exception. Appending {} to domains to query.".format(domain))
                to_try.append(row)
                retry_counter += 1
                time.sleep(backoff * 60)
                if backoff < 30:
                    backoff *= 4
                else:
                    backoff = 30
                continue

        if "categories" in j:
            categories = "|".join(j["categories"])
        else:
            categories = "uncategorized"
        verbose_msg = j["verbose_msg"]
        out_row = row + [categories] + [verbose_msg]
        csv_writer.writerow(out_row)
        outfh.flush()
        time.sleep(1)
