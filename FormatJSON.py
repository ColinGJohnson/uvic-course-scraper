'''
This is just a python program that takes a json file and formats it in a different way
'''

import json, sys

try:
    fp = open(sys.argv[1] + '.json', 'r')
    courses_file = open(sys.argv[1] + '_courses.json', 'w')
    crn_file = open(sys.argv[1] + '_crn.json', 'w')
except:
    print("Invalid file")

courses = json.load( fp )

# print(courses[0])
courses_output = []
crn_output = []

for course in courses:
    # First we must format the courses file
    title = course["course_title"]
    subject = course["subject"]
    course_code = course["course_code"]
    term = course["term"]
    term_string = course["term_string"]
    levels = course["levels"]
    sections_raw = course["sections"]
    sections = []

    for section in sections_raw:
        sections.append( section["crn"] )

        # Here we will format the CRN file
        crn_output.append(
            {
                'crn':section["crn"],
                'description':section["description"],
                'section_type':section['section_type'],
                'section_number':section["section_number"],
                'reg_start':section["reg_start"],
                'reg_end':section["reg_end"],
                'attributes':section["attributes"],
                'campus':section["campus"],
                'schedule_type_alt':section["schedule_type_alt"],
                'method':section["method"],
                'credits':section["credits"],
                'catalog_entry':section["catalog_entry"],
                'meeting_times':section["meeting_times"],
            }
        )

    
    courses_output.append( 
        {
            'course_title':title, 
            'subject':subject, 
            'course_code':course_code,
            'term':term,
            'term_string':term_string,
            'levels':levels,
            'sections':sections
        }
    )

json.dump( 
    courses_output,
    courses_file,
    indent=4
)

json.dump(
    crn_output,
    crn_file,
    indent=4
)