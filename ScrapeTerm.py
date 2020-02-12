from os import listdir
from datetime import datetime
import re
import json

import bs4
from bs4 import BeautifulSoup
from robobrowser import RoboBrowser

debug = False;

def main():
	
    # get number of terms to collect data for
	target_term = input("Collect data from which term? eg. 201901 ('all' to collect all): ")

	# get file name
	database_name = input("enter a database name (WILL BE OVERWRITTEN!): ")

	# collect data for those terms
	if (target_term.lower() == 'all'):
		courseData = scrapeTerms(num_terms=-1)
	else:
		courseData = scrapeTerms(requested_term=target_term)

	# save the data in json format
	filename = database_name + '.json'
	with open(filename, 'w') as file:
		try:
			file.write(json.dumps(courseData, indent=4))
			print(filename + ' saved')
		except Exception as e:
			print("Could not save file! ", e)

	# print completion message
	print('page collection complete')

	# end of main function
	return


def scrapeTerms(num_terms=1, requested_term="", saveHtml=False):

	# define a list for course information
	courses = []

	# create a new browser to navigate search forms
	browser = RoboBrowser(parser='html.parser')

	# open course search page and get term options
	browser.open('https://www.uvic.ca/BAN1P/bwckschd.p_disp_dyn_sched')
	term_options = browser.find_all("option")

	if (debug): 
		found_terms = []
		for term_option in term_options:
			found_terms.append(term_option['value'])
		print("found terms: " + str(found_terms))

	# iterate through data for all terms
	for term_option in term_options:

		# isolate term value
		term = term_option['value']

		# skip empty form values
		if len(term) == 0:
			continue

		# collect only the requested amount of data
		if (requested_term != "" and term != requested_term):
			continue

		if num_terms == 0:
			break
		else:
			num_terms -= 1
			print('COLLECTING FROM TERM ' + term + ". \n")
		
		# get, fill, and submit the search form (there is only one form on this page)
		term_form = browser.get_form()
		term_form['p_term'].value = term
		browser.submit_form(term_form)

		# get a list of all available subjects
		subject_dropdown = browser.find('select', attrs={"name": "sel_subj"})
		for subject_option in subject_dropdown.find_all("option"):

			# isolate subject abbreviation
			subject = subject_option['value']

			# get, fill, and submit the class schedule form
			schedule_form = browser.get_form()
			schedule_form.fields.getlist('sel_subj')[1].value = subject
			browser.submit_form(schedule_form)

			# save the the search result page
			result = str(browser.parsed())

			if saveHtml:
				filename = 'ResultPages\\' + term + subject + '.html'
				with open(filename, 'w') as file:
					try:
						file.write(result)
						print(filename + ' downloaded')
					except Exception as e:
						print("Could not save file! ", e)

			# parse the resulting html string
			print('Parsing ' + term + subject + '.html ... ', end="")
			subject_courses = parse(result, term)

			for subject_course in subject_courses:
				courses.append(subject_course)

			# go back to the class search form
			browser.back(1)

		# go back to the term selection form
		browser.back(1)

	# return from scrapeTerms
	return courses


'''Returns a list of dictionaries containing information for each course listed in the given html file'''
def parse(html, term):

	# read current html file into beautifulsoup
	soup = BeautifulSoup(html, 'html.parser')

	# create a new data structure for course information
	courses = []

	# find the all the headers for all of the search results
	for table_header in soup.find("table", class_="datadisplaytable").find_all("th", class_="ddtitle"):

		# construct a dictionary with default values to store information about this course listing
		course = {	
			"course_title": "",
			"subject": "",
			"course_code": "",
			"term": term,
			"term_string": "",
			"levels": "",
			"sections": [
				{	
					"crn": "",
					"description": "",
					"section_type": "",
					"section_number": "",
					"reg_start": "",
					"reg_end": "",
					"attributes": "",
					"campus": "",
					"schedule_type_alt": "",
					"method": "",
					"credits": "",
					"catalog_entry": "",
					"meeting_times": [],
				}
			]
		}

		# isolate a string of the course listing header
		header_contents = table_header.a.contents[0]

		# remove dashes in course title if there are too many
		hyphen_count = header_contents.count(' - ')
		if hyphen_count > 3:
			header_contents = header_contents.replace(' - ', '', hyphen_count - 3)

		# split the header by dashes (four elements)
		header_data = header_contents.split(' - ')

		# transform the header data into the database format
		course['course_title'] = header_data[0] # course title
		course['sections'][0]['crn'] = header_data[1] # crn
		course['subject'] = header_data[2].split(' ')[0] # subject eg. chem
		course['course_code'] = header_data[2].split(' ')[1] # course code
		course['sections'][0]['section_type'] = header_data[3][0] # section type (a, b, or t)
		course['sections'][0]['section_number'] = header_data[3][1:] # section number

		# find next <tr> after table header's parent <tr> which contains the rest of the course info
		row_after = table_header.parent.find_next("tr").td

		# get the course description
		description = row_after.contents[0].strip()
		course['sections'][0]['description'] = description if len(description) > 0 else "No Description"

		# get the catalog entry
		course['sections'][0]['catalog_entry'] = "{0}{1}".format("https://www.uvic.ca", row_after.find("a")["href"])



		# create a list of strings from the information displayed below the header and above the catalog link, "middle info"
		middle_info = []
		for string in row_after.stripped_strings:
			middle_info.append(string)

		# remove meeting times table and catalog link from list
		for i in range(len(middle_info)):
			if middle_info[i] == "View Catalog Entry":
				middle_info = middle_info[:i]
				break

		# get the fields that are *maybe* there
		for i in range(len(middle_info) - 1):

			if middle_info[i] == "Registration Dates:":
				
				# split the given registration date range into two ISO 8601 date strings
				split_dates = middle_info[i + 1].split(" to ") 

				if len(split_dates) == 2:
					course['sections'][0]['reg_start'] = datetime.strptime(split_dates[0], "%b %d, %Y").isoformat()
					course['sections'][0]['reg_end'] = datetime.strptime(split_dates[1].strip(), "%b %d, %Y").isoformat()

			elif middle_info[i] == "Associated Term:":
				course['term_string'] = middle_info[i + 1]

			elif middle_info[i] == "Levels:":
				course['levels'] = middle_info[i + 1]

			elif middle_info[i] == "Attributes:":
				course['sections'][0]['attributes'] = middle_info[i + 1]


		# get last four elements of the middle info (credits, instructional method, schedule type, campus)
		course['sections'][0]['campus'] = middle_info[-4]
		course['sections'][0]['schedule_type_alt'] = middle_info[-3]
		course['sections'][0]['method'] = middle_info[-2]
		course['sections'][0]['credits'] = middle_info[-1]



		# get <tr> elements from the "scheduled meeting times" table with a CSS selector
		meeting_time_rows = row_after.select("table > tr")[1:]

		# we will store information about each meeting time for this course in a list of dictionaries
		meetings = []

		# if there are scheduled meeting times (1 per row), add their details to data2
		for row in meeting_time_rows:

			# assign default values to the rowdata array
			rowdata = [""] * 6
			
			# iterate through all of the data in the current <tr>, except instructors
			tds = row.select("td")
			for i in range(0, len(tds) - 1):

				# get the contents of the tag
				entry = tds[i].string

				# if entry is blank, and <abbr> tag or a special character, replace with TBA
				if isinstance(entry, bs4.element.Tag) or entry == "\xa0":
					entry = "TBA"

				# add the collected information to list of information on the current row
				rowdata[i] = entry

			# parse the instructors column, collecting name/email pairs in JSON format from each <a> tag
			instructor_links = tds[6].find_all("a")
			instructor_data = [{"name": "TBA", "email": "TBA"}]

			if len(instructor_links) != 0:
				instructor_data = []
				for instructor_link in instructor_links:
					instructor_data.append({"name": instructor_link["target"], "email": instructor_link["href"].split(":")[1]})

			# split the given date range ex. "Jan 07, 2019 - Apr 05, 2019" into two ISO 8601 date strings
			split_dates = rowdata[4].split(" - ")
			start_date = ""
			end_date = ""

			if len(split_dates) == 2:
				start_date = datetime.strptime(split_dates[0].strip(), "%b %d, %Y").isoformat()
				end_date = datetime.strptime(split_dates[1].strip(), "%b %d, %Y").isoformat()

			# assign default values to the meeting dictionary
			meeting = {
				"type":			 rowdata[0],
				"time":		 	 rowdata[1],
				"days":		 	 rowdata[2],
				"location": 	 rowdata[3],
				"start_date":	 start_date,
				"end_date":		 end_date,
				"schedule_type": rowdata[5],
				"instructors": 	 instructor_data,
			}

			# add ths meeting time to the list of meeting times for the current course
			meetings.append(meeting)

		# add the current course's meetings to the list of all course meetings
		course['sections'][0]['meeting_times'] = meetings

		# check if another section of this course has been parsed already, if it has been,
		# add this section to that previous course's sections list.
		already_found = False
		for previous_course in courses:
			if previous_course['course_title'] == course['course_title']:
				previous_course['sections'].append(course['sections'][0])
				already_found = True

		# add the current course's  data to the list of all course data
		if already_found == False:
			courses.append(course)

	# return from function
	print('Identified {} course listing(s).\n'.format(len(courses)))
	return courses

# TODO: LEGACY SQLITE FUNCTION, STILL NEEDS TO BE MAPPED TO NEW JSON OUTPUT FORMAT
def outputDatabase(database_name, data):

	# open course database connection
	conn = sqlite3.connect("{}.db".format(database_name))

	# cursor to execute sqlite3 commands
	c = conn.cursor() 

	# create lists of items to insert into each database row
	data1 = []
	data2 = []

	# insert collected data into courses table
	try:
		c.execute("INSERT INTO courses VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(data1))
		
		for row in data2:
			c.execute("INSERT INTO meeting_times VALUES (?,?,?,?,?,?,?,?)", tuple(row))

	# catch database exceptions
	except Exception as e:
		print('SQL error: "{0}"'.format(e))

	# create course databases
	c.execute('DROP TABLE IF EXISTS courses')
	c.execute('DROP TABLE IF EXISTS meeting_times')
	c.execute('CREATE TABLE courses(crn number PRIMARY KEY, name text, subject text, course_code text, section_type text, section_number number, description text, term text, reg_dates text, levels text, attributes text, campus text, schedule_type_alt text, method text, credits text, catalog_entry text)') 
	c.execute('CREATE TABLE meeting_times(crn number, meeting_type text, meeting_time text, days text, location text, date_range text, schedule_type text, instructor text)') 

	# commit database changes
	conn.commit()

	# close course database connection
	conn.close()

	# return from outputDatabase
	return

# if this file isn't being imported, run automatically 
if __name__ == "__main__":
    main()