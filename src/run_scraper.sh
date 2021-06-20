#!/bin/bash

# 05 -> Summer, 09 -> Fall, 01 -> Spring
export TERM="202101"

# activate python virtual environment (env is assumed to exist and have all requirements)
source env/bin/activate

# clean up previous temp files
mkdir html

# scrape search result pages
#echo "Scraping $TERM..."
#python3 ./Scraper.py --term=$TERM

# parse the search result pages into more useful json
#echo "Parsing $TERM..."
#python3 ./Parser.py --term=$TERM

# upload changes to mongodb MONGODB_STR should be set in system environment variables
for filename in ./json/*.json; do
    echo "Uploading term data from $filename..."
    #python3 ./Uploader.py --input="$filename"
done

echo "Course scraping complete!"
