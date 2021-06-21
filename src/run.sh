#!/bin/bash

# exit on errors
set -e

# 05 -> Summer, 09 -> Fall, 01 -> Spring
# Currently this line should be manually updated when a new schedule is released
TERMS=('202105' '202109' '202201')

for term in "${TERMS[@]}"; do

    # download search result pages as HTML
    python3 ./Scraper.py --term=$term

    # parse the search result HTML into more useful json
    echo "Parsing $term..."
    python3 ./Parser.py --term=$term
done

# upload course data to 
for filename in ./json/*.json; do
    echo "Uploading data from $filename..."
    python3 ./Uploader.py --input="$filename"
done

echo "Course scraping complete!"
