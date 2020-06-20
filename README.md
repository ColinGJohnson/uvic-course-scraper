# UVic Course Data Scraper

"uvic-course-scraper" is a Python 3 web scraping script which makes use of [RoboBrowser](https://robobrowser.readthedocs.io/en/latest/) and [Beautiful Soup 4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) gather data on current and past courses at the University of Victoria through [uvic.ca](https://www.uvic.ca/) and store those data in a json database file.

**This project relies on the current HTML structure of the University of Victoria website, since I have no control over changes to that site, this script may some day break completely with no warning.**

## Purpose
UVic's current public [class schedule search](https://www.uvic.ca/BAN1P/bwckschd.p_disp_dyn_sched) is archaic, and their schedule building tools are worse still. The first step towards developing better third party options for students is obtaining a detailed and accurate course database.

## Usage
The web scraping script is intended to by run via command line in a python 3.x environment with the dependencies specified in *requirements.txt* installed via pip. An example .json output file, 'example.json' is included in the repo.

## Future Features
* Better command-line parameters for automation using shell scripts instead of the current interactive CLI approach.
* Launch parameter to output SQLite3 instead of JSON
* Refactor code to more easily handle changes to the UVic website

## EC2 setup
- create new t2.micro vm with ubuntu 18.04 lts + 8gb ebs volume
- ssh into vm
- generate new ssh key and add to gitlab account
- clone scraper git repo and cd into it
- install python3.8
- update python3 command to use python3.8
- install pip3
- install venv: sudo apt install python-virtualenv
- install virtualenv: python3 -m pip install --user virtualenv
- create new python virtual env: python3 -m venv --without-pip env
- activate the virtual env: source env/bin/activate
- install pip in the virtual env: curl https://bootstrap.pypa.io/get-pip.py | python3
- install scraper script requirements: pip3 install -r requirements.txt
- set the following environment variables: 
    sudo -H gedit /etc/environment
    add "MONGODB_STR=<mongodb connection string>"
- scheduler scraper script as cron job
