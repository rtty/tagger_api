# Generating Relevant Tag Objects for Projects

- A API based tool that create and maintain project tags.

## Tech Stack

- [Django](https://www.djangoproject.com/)
- [Djangorestframework](https://www.django-rest-framework.org/)
- [DynamoDB](https://aws.amazon.com/dynamodb/)

# Docker Deployment:

- Ensure that the 'contest-tagging API' has already been deployed and its url available.
- Replace (if required) the URL in the Dockerfile (inside the folder project_tool) ENV ENV_TAGGING_API_BASE_URL
  variable with the URL of the contest-tagging API.
- cd to root folder. Run the following command:

```bash
    docker network create COMPANY_API_NET
    docker-compose -f docker-compose-local.yml up --build
```

- Create dynamoDB tables. Run the following command:

```bash
    cd project_tool/API/project_tags/
    source ../env_export.bash
    pip install -r requirements.txt
    pip install -e ../../../bus-api-wrapper-python 
    python manage.py create_tables
```

# Deployment without Docker:

## Installation and Running locally

- Please follow the project_tool_starter_guide.md

## API SOLUTION MODULES

### RAW TAGGING MODULE

- python file - raw_tagging_service.py
- Fetches projects from API using the lastRefreshedAt value stored in db of the last run.
- This module has two usages -

1. Call the tagging tool to tag all the projects and save them to DB
2. tag specific projects based on ids and save them to DB

- Calls the tagging tool based on the configuration present in tagging_config.json

### DATABASE MODULE

- python file - database_service.py
- Interacts with the db and related operations and contains function for those db operations called by other modules
- Currently dynamoDB is used for the solution with two tables - one for storing the projects and other for the members
  along with the lastRefreshedAt value.

# Database management

- Create dynamoDB tables. Run the following command:

```bash
    cd project_tool/API/project_tags/
    source ../env_export.bash
    python manage.py create_tables
```

or

```bash
    docker-compose -f docker-compose-local.yml exec project-tag-update python manage.py create_tables
```

- Drop dynamoDB tables. Run the following command:

```bash
    cd project_tool/API/project_tags/
    source ../env_export.bash
    python manage.py drop_tables
```

or

```bash
    docker-compose -f docker-compose-local.yml exec project-tag-update python manage.py drop_tables
```

- View dynamoDB tables. Run the following command:

```bash
    cd project_tool/API/project_tags/
    source ../env_export.bash
    python manage.py view_data project_details
```

```bash
    cd project_tool/API/project_tags/
    source ../env_export.bash
    python manage.py view_data project_details --id 2a632101-805f-4385-ac20-8450e999d7a4
```

# Verification

## Set variables:

In ENV_AUTH0_CLIENT_ID replace <client id> with `<client id>`
In ENV_AUTH0_CLIENT_SECRET replace <client secret> with `<client secret>`

## New Postman

- Import Postman collection and variables:
  `docs/project_tags.postman/project_tags.postman_collection.json`
  `docs/project_tags.postman/project_tags.postman_environment.json`
- Execute calls in `project_tags` folder

### Pagination, new `Skill` parameter, authorization

Can be verified using Postman. GET endpoints have additional pagination information in the response.

## Bus Event Verification

- login `https://lauscher.example-dev.com/` with credential `user1 / user1`
- then select topic to view, skills.notification.get or skills.notification.update in Topics field, then click `View`
  button to view related messages

## CHANGELOG - #1

- `update_project_tags.py` file has been modified to accept multple project ids as a list instead of comma separated
  strings. The value comes to the server as a string (eg. "['abc', 'def']"), so we had to process this string and
  extract the project ids from it (so that it looks like ['abc', 'def'])

- Postman file is updated accordingly

- the old app is removed to avoid confusion. Any reference to the skill extractor is removed and information about the
  project tag update app is added

## CHANGELOG - #2

- create/drop table script added which only deals with project details table
- swagger file generation issue fixed in settings.py

## CHANGELOG - #3

- added new query param `status` to the GET end-point, so that project recommender tool can get the open project
  list
- `get_project_tags.py` is updated to get the open project ids from the project api, and those ids are used to get
  project tags from the project details table.
- new entry in the postman collection to test the `status` query param
- swagger file updated accordingly



