from os import listdir
from os import makedirs
import time as t
import argparse
import re
import json
import bs4
from bs4 import BeautifulSoup
from robobrowser import RoboBrowser
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *

def main():
	'''
	Processes command-line arguments if this script is being run directly.
	'''

	parser = argparse.ArgumentParser(
		description=("Scrape course information from the UVic website. "
		"If a specific term is not specified, the most recent term will be scraped."))

	parser.add_argument("--term",
		help=("First month of the term to scrape formatted as YYYYMM, "
		"e.g. 201901. Second term = 01, Summer Session = 05, First Term = 09."))

	parser.add_argument(
		"--all", 
		help="When true, scrape all course results for all available terms.",
		type=bool,
		default=False
	)

	args = parser.parse_args()
	scraper = SearchFormScraper()

	if args.all:
		scraper.scrapeSearchForm()
	elif args.term is not None:
		scraper.scrapeSearchForm(requested_term=args.term)
	else:
		scraper.scrapeSearchForm(first_only=True)
	return

class SearchFormScraper:
	'''
	Scrapes course information for a specific term, or number of terms by traversing UVic's
	course search interface and passing search result pages to parse().
	'''

	def __init__(self, output_directory="./html/"):
		self.output_directory = output_directory
		return

	def scrapeSearchForm(self, requested_term=None, first_only=False):

		# create a new browser to navigate search forms
		browser = RoboBrowser(parser='html.parser')

		# open course search page and get term options (option tag values)
		browser.open('https://www.uvic.ca/BAN1P/bwckschd.p_disp_dyn_sched')
		term_options = browser.find_all("option")

		# iterate through the available terms
		for term in [option['value'] for option in term_options]:

			# scrape only the requested term, if one was requested
			if not term or (requested_term and term != requested_term):
				continue
			
			print(f"Collecting data for term '{term}'...")

			# get, fill, and submit the search form (there is only one form on this page)
			term_form = browser.get_form()
			term_form['p_term'].value = term
			browser.submit_form(term_form)

			# get a list of all available subjects
			subject_dropdown = browser.find('select', attrs={"name": "sel_subj"})
			for subject_option in subject_dropdown.find_all("option"):

				# isolate subject abbreviation
				subject = subject_option['value']
				print(f"Selected subject'{subject}'")

				# get, fill, and submit the class schedule form
				schedule_form = browser.get_form()
				schedule_form.fields.getlist('sel_subj')[1].value = subject
				browser.submit_form(schedule_form)

				# save the search result page as HTML
				result_html = str(browser.parsed())

				date_today = datetime.now().date().strftime('%Y%m%d')
				directory = f"{self.output_directory}{date_today}/{term}"
				filename = f"{directory}/{subject}_{term}_{date_today}.html"

				makedirs(directory, exist_ok=True)
				with open(filename, 'w') as file:
					try:
						file.write(result_html)
						print(f"Saved course search result as '{filename}'")
					except Exception as e:
						print(f"Failed to save '{filename}': ", e)

				# wait for a second to avoid rate limiting
				t.sleep(1)

				# go back to the class search form
				browser.back(1)

			# stop here if we are only getting data from the most recent term
			if first_only:
				return

			# go back to the term selection form
			browser.back(1)
		return

if __name__ == "__main__":
	main()
