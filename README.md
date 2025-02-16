> [!CAUTION]
> UVic has replaced their schedule search page! This script is no longer functional.

# UVic Course Data Scraper

"uvic-course-scraper" is a Python 3 web scraping script which makes use of [RoboBrowser](https://robobrowser.readthedocs.io/en/latest/) and [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) gather data on current and past courses at the University of Victoria through [uvic.ca](https://www.uvic.ca/) and store those data in a json database file.

**This project relies on the current HTML structure of the University of Victoria website, since I have no control over changes to that site, this script may some day break completely with no warning.**

## Purpose

UVic's current public [class schedule search](https://www.uvic.ca/BAN1P/bwckschd.p_disp_dyn_sched) is archaic, and their schedule building tools are worse still. The first step towards developing better third party options for students is obtaining a detailed and accurate course database.

## Usage

The course data collection is divided into three python scripts: `Scraper.py` downloads course search result pages as HTML, `Parser.py` pulls data out of that HTML and save it as JSON, and `Uploader.py` pushes that JSON course data to the DynamoDB though our AppSync API.

The three python scripts are run through the `run.sh` shell script which is in turn intended to be executed in a docker container. Typically the docker image is built in the GitLab CI pipeline and run on AWS Fargate, but for testing purposes it can be built and run locally; you must have Docker installed to do this.

### Build the scraper docker image

```bash
docker build -t course-scraper .
```

### Run the scraper image locally

```bash
docker run --memory="4g" course-scraper
```
