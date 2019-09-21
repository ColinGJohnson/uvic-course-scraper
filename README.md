# UVic Course Data Scraper
"uvic-course-scraper" is a Python 3 web scraping script which makes use of [RoboBrowser](https://robobrowser.readthedocs.io/en/latest/) and [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) gather data on current and past courses at the University of Victoria through [uvic.ca](https://www.uvic.ca/) and store those data in a json database file.

**This project relies on the current funcionality of the University of Victoria website, since I have no control over changes to that site, this script may break completely some day with no warning.**

## Purpose
UVic's current public [class schedule search](https://www.uvic.ca/BAN1P/bwckschd.p_disp_dyn_sched) is archaic, and their schedule building tools are worse still. The first step towards developing better third party options for students is obtaining a detailed and accurate course database.

## Usage
The web scraping script is intended to by run via command line in a python 3.x environment with the dependencies specified in *requirements.txt* installed via pip.
