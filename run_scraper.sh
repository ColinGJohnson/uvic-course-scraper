# the term to scrape data for
# this should always be set to whatever the "current" term people are resgistering for is.
export TERM="202005"
export LOGFILE="~/log.txt"

# make sure we are in the right directory
cd ~/uvic-course-scraper

# activate python virtual environment (env is assumed to exist and have all requirements)
source env/bin/activate

# clean up previous results
echo "Removing html/json from previous runs..."
rm -rf html/ json/

# scrape search result pages
echo "Scraping $TERM..."
python3 ./Scraper.py --term=$TERM >> $LOGFILE

# parse the search result pages into more useful json
echo "Parsing $TERM..."
python3 ./Parser.py  >> $LOGFILE

# upload changes to mongodb MONGODB_STR should be set in system environment variables
for filename in ./json/*.json; do
    echo "Uploading $TERM..."
    python3 ./Uploader.py --input="./json/$TERM.json" --constr="$MONGODB_STR" >> $LOGFILE
done

echo "Course scraping complete!"
