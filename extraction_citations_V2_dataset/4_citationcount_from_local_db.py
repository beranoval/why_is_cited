import sqlite3
import csv

#### Takes previously produced metadata+citations database and creates a CSV file
#### that has articles grouped by DOI, year and citation count.
#### Question marks in result indicate that the OCI database knows the DOI, but has no associated citations in the
#### database dump.


con = sqlite3.connect('oci_extract_years.db')
cur_citations = con.cursor()

outfile = "citationcounts_oci_revised_year.csv"

with open('pmc_doi.csv', 'r', encoding="utf-8") as read_obj:
    csv_reader = csv.reader(read_obj)
    next(csv_reader)

    with open(outfile, mode='w', encoding="utf-8", newline='') as out:
        writer = csv.writer(out, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerow(["doi", "pmc", "name", "count_opencitations", "year"])

        for row in csv_reader:
            print(row)

            name = row[0]
            pmc = row[1]
            doi = row[2]

            print(doi)
            cur_citations.execute("select count(*) from articles WHERE doi = ?", (doi, ))
            exists = cur_citations.fetchone()[0]

            if exists:
                cur_citations.execute("select year, count(*) as count from cites WHERE doi_target = ? GROUP BY year", (doi, ))
                res = cur_citations.fetchall()

                for row in res:
                    writer.writerow([ doi, pmc, name, row[0], row[1] ])

                print(res)
            else:
                writer.writerow([ doi, pmc, name, "?", "?" ])
    
 
