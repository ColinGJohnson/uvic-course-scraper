import pymongo
import argparse
from pprint import pprint

import json

def main():

	parser = argparse.ArgumentParser(
		description="Upload scraped course data to a mongodb cluster."
	)

	parser.add_argument("--input", 
		help="JSON file which with to update the course documents.",
		type=str,
		required=True
	)

	parser.add_argument("--constr",
		help=("MongoDB connection string to connect to the database with."),
		type=str,
		required=True
	)

	parser.add_argument("--database",
		help=("Database to use."),
		type=str,
		default="schedulerdb"
	)

	parser.add_argument("--collection",
		help=("Collection to use."),
		type=str,
		default="courses"
	)

	args = parser.parse_args()

	# read the specified file as json
	with open(args.input, 'r') as file:
		try:
			jsonstr = file.read()
		except Exception as e:
			print("Error while reading input file: ", e)

	data = json.loads(jsonstr)
	print(f'Found {len(data)} items in input file.')

	# connect to MongoDB
	client = pymongo.MongoClient(args.constr)
	database = client[args.database]
	collection = database[args.collection]

	# iterate over all the courses in the input file
	updated = 0
	inserted = 0

	for course in data:

		# find the course to update by term and crn
		query = { 
			'course_title': course['course_title'],
			'subject': course['subject'],
			'course_code': course['course_code'],
			'term': course['term']
		}

		# create/update the course listing
		result = collection.update_one(query, { '$set': course }, upsert=True)

		if result.upserted_id is not None:
			print(f'inserted {course["term"]} {course["subject"]}-{course["course_code"]}: {course["course_title"]}')
			inserted += 1

		elif result.modified_count == 1:
			print(f'updated {course["term"]} {course["subject"]}-{course["course_code"]}: {course["course_title"]}: ')
			updated += 1

	print(f'SUMMARY: updated {updated}, inserted {inserted}')

# if this file isn't being imported, run automatically
if __name__ == "__main__":
	main()
