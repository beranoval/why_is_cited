import csv
import requests
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

##### This script fetches DOIs for PMC identifiers from the previous script.
##### Input of this script is a file generated by 1_extract_pmc.py.
##### Output is the combination of the fields in the previous script (title, pmcid) and DOI.
##### PMC to DOI API is used with time delays to not put any great stress on the free API.
##### If you modify this script, remember to use appropriate delays between API calls.

s = requests.Session()

retries = Retry(total=5,
                backoff_factor=1,
                status_forcelist=[ 500, 502, 503, 504 ])

s.mount('https://', HTTPAdapter(max_retries=retries))


outfile = "pmc_doi.csv"

def append_dois(lines):
    global s

    keys = list(lines.keys())

    r = s.get(
        "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/?ids=" + (','.join(keys)) + "&idtype=pmcid&format=json&versions=yes&showaiid=no&tool=Covid19Citations&email=  &.submit=Submit"
    )

    json = r.json()

    for record in json["records"]:
        if "doi" in record:
            lines[record["pmcid"]].append(record["doi"])
        else:
            lines[record["pmcid"]].append("")

with open('pmc_articlenames.csv', 'r', encoding="utf-8") as read_obj:
    csv_reader = csv.reader(read_obj)

    lastlines = {}

    with open(outfile, mode='w', encoding="utf-8", newline='') as out:
        writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(
            [
                "title",
                "pmcid",
                "doi"
            ]
        )
        
        for row in csv_reader:
            lastlines[row[1]] = [
                row[0],
                row[1]
            ]

            if len(lastlines) >= 100:
                time.sleep(2)
                append_dois(lastlines)
                
                for key, value in lastlines.items():
                    writer.writerow(
                        value
                    )
                    
                lastlines = {}

        if len(lastlines) > 0:
            append_dois(lastlines)
            
            for key, value in lastlines.items():
                writer.writerow(
                    value
                )


