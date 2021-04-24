import time
import datetime
import json
import argparse
import os

from dotenv import load_dotenv
from requests_aws4auth import AWS4Auth
import requests

# parse arguments and load environment variables
parser = argparse.ArgumentParser(
    description="Upload course data to DynamoDB."
)

parser.add_argument("--input", 
    help="JSON file which with to update the course documents.",
    type=str,
    required=True
)

args = parser.parse_args()
load_dotenv()

# Use AWS4Auth to sign a requests session 
# (see: https://pypi.org/project/requests-aws4auth/)
# (see: https://stackoverflow.com/questions/60293311/how-to-send-a-graphql-query-to-appsync-from-python)
session = requests.Session()
session.auth = AWS4Auth(
    os.getenv('AWS_ACCESS_KEY_ID'),
    os.getenv('AWS_SECRET_KEY'),
    'us-west-2',
    'appsync'
)

# found in AWS Appsync under Settings for the course scheduler endpoint.
APPSYNC_API_ENDPOINT_URL = os.getenv('APPSYNC_URL')


def send_graphql_query(session, query):
    response = session.request(
        url=APPSYNC_API_ENDPOINT_URL,
        method='POST',
        json={'query': query}
    )

    if response.status_code != 200:
        print(query)
        print(response.json())
        raise Exception(f"Query failed, response code: {request.status_code}.")
        return None

    return response.json()


def check_course_exists(session, term, subject, course_code):
    check_course_existance_query = f"""
    query MyQuery {{
        coursesByCode(
            subjectCourse_code: {{
                beginsWith: {{
                    course_code: "{course_code}", 
                    subject: "{subject}"
                }}
            }}, 
            term: "{term}"
        ) {{
            items {{
                id
                course_code
                term
                subject
            }}
        }}
    }}
    """

    response = send_graphql_query(session, check_course_existance_query)
    items = response['data']['coursesByCode']['items']
    
    if len(items) > 1:
        raise Exception(f"Duplicate course found with query: {check_course_existance_query}")

    return None if len(items) == 0 else items[0]['id']


def dict_to_graphql_mutation_input(object, level=0):
        fields = []
        for key in object.keys():
            value_type = type(object[key])

            if (value_type is list):
                list_fields = []
                for item in object[key]:
                    list_fields.append(dict_to_graphql_mutation_input(item, level=level+1))
                fields.append(f'{key}: [{", ".join(list_fields)}]')

            elif(value_type is str):
                value = object[key].replace('\n', ' ').replace('"', '\\"')
                fields.append(f'{key}: "{value}"')

            elif(value_type is int):
                fields.append(f'{key}: "{str(value)}"')

            else:
                raise Exception(f"This function only works for str, int and list, not {type(object[key])}")

        result = f"{{{' '.join(fields)}}}"
        return f"input: {result}" if level == 0 else result


# read the specified file as json
with open(args.input, 'r') as file:
    try:
        jsonstr = file.read()
    except Exception as e:
        print("Error while reading input file: ", e)
data = json.loads(jsonstr)
print(f'Found {len(data)} items in input file.\n')

# iterate over all the courses in the input file
updated = 0
inserted = 0
for progress, course in enumerate(data):

    # check if the course already exists in the database
    id = check_course_exists(session, course['term'], course['subject'], course['course_code'])

    # update the existing course if it exists, otherwise create it
    action = ""
    if id:
        course['id'] = id
        action = "updateCourse"
        updated += 1
        
    else:
        action = "createCourse"
        inserted += 1

    # make the mutation
    mutation = f"""
    mutation CourseUpload {{
        {action}({dict_to_graphql_mutation_input(course)}) 
        {{
            id
        }}
    }}
    """
    response = send_graphql_query(session, mutation)
    
    # check for any errors
    if ("errors" in response):
        raise Exception(f"Mutation failed: {mutation} with response {response}")

    # print a summary of the changes
    change = "Updated" if id else "Created"
    print(f"({progress}/{len(data)})")
    print(f'{change} {course["term"]} {course["subject"]}-{course["course_code"]}: {course["course_title"]}')
    print(response, "\n")

print(f'SUMMARY: updated {updated}, inserted {inserted}')
