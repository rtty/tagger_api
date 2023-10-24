import json
import logging
from collections import OrderedDict

import django
import requests
from tqdm import tqdm

from .database_service import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


def remove_duplicate_tags(response):
    """remove duplicates from within a tag type as well in between multiple tags type"""
    seen = {
        "required_skill": [],
        "summary_phrases": [],
        "problem_domain": [],
        "target_audience": [],
    }
    all_seen = []
    results = []
    for tags in response:
        if tags["tag"].lower() not in seen[tags["type"]] and tags["tag"].lower() not in all_seen:
            seen[tags["type"]].append(tags["tag"].lower())
            all_seen.append(tags["tag"].lower())
            results.append(tags)
    results = sorted(results, key=lambda i: i["type"])

    return results


def get_tags(data, config):
    """returns a list of tags for a given input of project"""

    base_url = config["api_base_url"]
    health_api_endpoint = base_url + "/v5/contest-tagging/health"
    logging.info(health_api_endpoint)
    results = []
    try:
        response = requests.get(health_api_endpoint)
        if response.status_code == 200:
            extract_confidence = config["extract_confidence"]
            if config["update_local_before_tagging"]:
                logging.info("Syncing EMSI Local file with Server!")
                update_local_emsi_api_endpoint = (
                    base_url + "/v5/contest-tagging/emsi/updated_local_emsi"
                )
                response = requests.post(update_local_emsi_api_endpoint)
                if response.status_code == 200:
                    logging.info(json.loads(response.text))
                else:
                    logging.info(json.loads(response.text))
            logging.info("Extracting Tags for projects!")
            for value in tqdm(data):
                result = {
                    "_id": value["project_id"],
                    "name": value["name"],
                    "startDate": value["startDate"],
                    "endDate": value["endDate"] if "endDate" in value else None,
                    "track": value["track"],
                    "appealsEndDate": (
                        value["appealsEndDate"] if "appealsEndDate" in value else None
                    ),
                    "winners": value["winners"] if "winners" in value else None,
                }
                tags = []
                try:
                    # get tags from external services
                    if config["tagging_emsi_type"].lower() == "external":
                        external_emsi_api_endpoint = base_url + "/v5/contest-tagging/emsi/external"
                        length = config.get("text_length", None)
                        response = requests.post(
                            external_emsi_api_endpoint,
                            data={
                                "text": value["project_spec"],
                                "length": length,
                                "extract_confidence": extract_confidence,
                            },
                        )
                        if response.status_code == 200:
                            tags.extend(json.loads(response.text))
                        else:
                            logging.info(json.loads(response.text))

                    # tags from internal file matching emsi
                    elif config["tagging_emsi_type"].lower() == "internal_refresh":
                        # internal matching with refresh
                        internal_refresh_emsi_api_endpoint = (
                            base_url + "/v5/contest-tagging/emsi/internal_refresh"
                        )
                        response = requests.post(
                            internal_refresh_emsi_api_endpoint,
                            data={
                                "text": value["project_spec"],
                                "extract_confidence": extract_confidence,
                            },
                        )
                        if response.status_code == 200:
                            tags.extend(json.loads(response.text))
                        else:
                            logging.info(json.loads(response.text))
                    elif config["tagging_emsi_type"].lower() == "internal_no_refresh":
                        # internal matching without refresh
                        no_internal_refresh_emsi_api_endpoint = (
                            base_url + "/v5/contest-tagging/emsi/internal_no_refresh"
                        )
                        response = requests.post(
                            no_internal_refresh_emsi_api_endpoint,
                            data={
                                "text": value["project_spec"],
                                "extract_confidence": extract_confidence,
                            },
                        )
                        if response.status_code == 200:
                            tags.extend(json.loads(response.text))
                        else:
                            logging.info(json.loads(response.text))
                    if config["enable_custom_tagging"]:
                        # custom tag extraction
                        custom_api_endpoint = base_url + "/v5/contest-tagging/custom"
                        response = requests.post(
                            custom_api_endpoint,
                            data={
                                "text": value["project_spec"],
                                "extract_confidence": extract_confidence,
                            },
                        )
                        if response.status_code == 200:
                            tags.extend(json.loads(response.text))
                        else:
                            logging.info(json.loads(response.text))
                    tags = remove_duplicate_tags(tags)
                    result["output_tag"] = tags
                except Exception as e:
                    logging.info("Error for key - %s", value["project_id"])
                    logging.exception(str(e))
                    result["output_tag"] = []
                results.append(result)
        else:
            logging.info("Tagging Server Unavailable!")
        return results
    except Exception as e:
        logging.exception(str(e))
        return []


def get_single_project(project_id):
    url = settings.CONFIG["project_base_url"] + "/v5/projects/" + project_id
    response = requests.request("GET", url, verify=False)
    if response.status_code == 200:
        r = json.loads(response.text)
        data = {}
        data = {
            "project_id": r["id"],
            "name": r["name"],
            "startDate": r["startDate"],
            "endDate": r["endDate"],
            "track": r["track"],
            "appealsEndDate": get_end_date(r),
            "project_spec": r["description"],
        }
        if "winners" in r:
            data["winners"] = r["winners"]
        return data
    else:
        logging.info("API unavailable!")
        return None


def get_projects(start_date):
    import json

    import requests

    if start_date:
        start_date = datetime.strftime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ").replace(":", "%3A")
        url = settings.CONFIG[
            "project_base_url"
        ] + "/v5/projects?page=1&perPage=100&status=Completed&updatedDateStart={}" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
            start_date
        )
    else:
        url = (
            settings.CONFIG["project_base_url"]
            + "/v5/projects?page=1&perPage=100&status=Completed&sortBy=updated&sortOrder=asc&isLightweight=false"
        )

    res = []

    response = requests.request("GET", url, verify=False)

    if response.status_code == 200:
        logging.info("Total No of pages = %s", response.headers["X-Total-Pages"])
        logging.info("Total No of projects = %s", response.headers["X-Total"])
        if int(response.headers["X-Total-Pages"]) <= 10:
            for i in tqdm(range(1, int(response.headers["X-Total-Pages"]) + 1)):
                if start_date:
                    url_pages = settings.CONFIG[
                        "project_base_url"
                    ] + "/v5/projects?page={}&perPage=100&status=Completed&updatedDateStart={}" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
                        i, start_date
                    )
                else:
                    url_pages = settings.CONFIG[
                        "project_base_url"
                    ] + "/v5/projects?page={}&perPage=100&status=Completed" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
                        i
                    )

                response = requests.request("GET", url_pages, verify=False)

                if response.status_code == 200:
                    temp = json.loads(response.text)
                    res.extend(temp)
        else:
            count = int(response.headers["X-Total-Pages"])
            while count > 10:
                for i in tqdm(range(1, 11)):
                    if start_date:
                        url_pages = settings.CONFIG[
                            "project_base_url"
                        ] + "/v5/projects?page={}&perPage=100&status=Completed&updatedDateStart={}" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
                            i, start_date
                        )
                    else:
                        url_pages = settings.CONFIG[
                            "project_base_url"
                        ] + "/v5/projects?page={}&perPage=100&status=Completed" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
                            i
                        )

                    response = requests.request("GET", url_pages, verify=False)

                    if response.status_code == 200:
                        temp = json.loads(response.text)
                        res.extend(temp)
                    else:
                        logging.info("%s %s", response.status_code, response.text)
                        logging.info("API unavailable!")

                if res:
                    temp = sorted(res, key=lambda i: i["updated"])
                    start_date = temp[-1]["updated"]
                    logging.info(start_date)
                    url = settings.CONFIG[
                        "project_base_url"
                    ] + "/v5/projects?page={}&perPage=100&status=Completed&updatedDateStart={}" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
                        i, start_date
                    )
                    response = requests.request("GET", url, verify=False)
                    if response.status_code == 200:
                        count = int(response.headers["X-Total-Pages"])
                    else:
                        logging.info("API unavailable!")
                else:
                    logging.info("API unavailable!")

            for i in tqdm(range(1, 11)):
                url_pages = settings.CONFIG[
                    "project_base_url"
                ] + "/v5/projects?page={}&perPage=100&status=Completed&updatedDateStart={}" "&sortBy=updated&sortOrder=asc&isLightweight=false".format(
                    i, start_date
                )
                response = requests.request("GET", url_pages, verify=False)
                if response.status_code == 200:
                    temp = json.loads(response.text)
                    res.extend(temp)
    else:
        logging.info("API unavailable!")
    logging.info("No of Projects Fetched: %s", len(res))
    return res


def get_projects_open(params=None):
    payload = {
        "page": "1",
        "perPage": "100",
        "status": "Active",
        "currentPhaseName": "Registration",
        "sortBy": "updated",
        "sortOrder": "asc",
        "isLightweight": "false",
    }
    if params is not None:
        payload["track"] = params["track"] if "track" in params else None
        payload["tracks[]"] = params["tracks[]"] if "tracks[]" in params else None
        payload["type"] = params["type"] if "type" in params else None
        payload["types[]"] = params["types[]"] if "types[]" in params else None
        payload["search"] = params["search"] if "search" in params else None
        payload["name"] = params["name"] if "name" in params else None
        payload["description"] = params["description"] if "description" in params else None

    res = []

    url = settings.CONFIG["project_base_url"] + "/v5/projects"
    response = requests.request("GET", url, params=payload, verify=False)

    if response.status_code == 200:
        logging.info("Total No of pages = %s", response.headers["X-Total-Pages"])
        logging.info("Total No of projects = %s", response.headers["X-Total"])
        if int(response.headers["X-Total-Pages"]) <= 10:
            for i in tqdm(range(1, int(response.headers["X-Total-Pages"]) + 1)):
                payload["page"] = i
                response = requests.request("GET", url, params=payload, verify=False)

                if response.status_code == 200:
                    temp = json.loads(response.text)
                    res.extend(temp)
        else:
            count = int(response.headers["X-Total-Pages"])
            while count > 10:
                for i in tqdm(range(1, 11)):
                    payload["page"] = i
                    response = requests.request("GET", url, params=payload, verify=False)

                    if response.status_code == 200:
                        temp = json.loads(response.text)
                        res.extend(temp)
                    else:
                        logging.info("%s %s", response.status_code, response.text)
                        logging.info("API unavailable!")
                if res:
                    temp = sorted(res, key=lambda i: i["updated"])
                    start_date = temp[-1]["updated"]
                    logging.info(start_date)
                    payload["page"] = i
                    payload["updatedDateStart"] = start_date
                    response = requests.request("GET", url, params=payload, verify=False)
                    if response.status_code == 200:
                        count = int(response.headers["X-Total-Pages"])
                    else:
                        logging.info("API unavailable!")
                else:
                    logging.info("API unavailable!")

            for i in tqdm(range(1, count + 1)):
                payload["page"] = i
                payload["updatedDateStart"] = start_date
                response = requests.request("GET", url, params=payload, verify=False)
                if response.status_code == 200:
                    temp = json.loads(response.text)
                    res.extend(temp)
    else:
        logging.info("API unavailable!")
    logging.info("No of Projects Fetched: %s", len(res))
    return res


def get_end_date(project):
    end_date = [p["actualEndDate"] for p in project["phases"] if "actualEndDate" in p]
    if end_date:
        end_date = max(end_date)
        try:
            end_date1 = datetime.strftime(
                datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ"),
                "%Y-%m-%dT%H:%M:%S.%fZ",
            )
            return end_date1
        except Exception:
            end_date2 = datetime.strftime(
                datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ"),
                "%Y-%m-%dT%H:%M:%S.%fZ",
            )
            return end_date2
    else:
        end_date3 = datetime.strftime(
            datetime.strptime(project["updated"], "%Y-%m-%dT%H:%M:%SZ"),
            "%Y-%m-%dT%H:%M:%S.%fZ",
        )
        return end_date3


def get_project_details(res):
    data = {}
    for r in res:
        data[r["id"]] = {
            "project_id": r["id"],
            "name": r["name"],
            "startDate": r["startDate"],
            "endDate": r["endDate"],
            "track": r["track"],
            "appealsEndDate": get_end_date(r),
            "project_spec": r["description"],
        }
        if "winners" in r:
            data[r["id"]]["winners"] = r["winners"]
    logging.info("Project details %s", len(data))
    return data


def get_data_from_api(last_refreshed_at):
    logging.info("Fetching data from API")
    res = get_projects(last_refreshed_at)
    data = get_project_details(res)
    return data


def get_data_from_api_open():
    logging.info("Fetching data from API")
    res = get_projects_open()
    data = get_project_details(res)
    return data


def get_env_variable(var_name):
    """Get the environment variable or return exception"""
    import os

    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"Set the {var_name} environment variable"
        raise django.core.exceptions.ImproperlyConfigured(error_msg)


def run_tagging_tool():
    """pull data from API and tag them"""

    last_refreshed_at = get_last_refreshed_at(settings.CONFIG["db_collection_projects"])
    logging.info("Last refreshed at %s", last_refreshed_at)
    if last_refreshed_at:
        # fetch only projects which are gt last_refreshed_at
        data = get_data_from_api(last_refreshed_at)
        if data:
            data = OrderedDict(
                sorted(
                    data.items(),
                    key=lambda x: x[1]["appealsEndDate"],
                    reverse=True,
                )
            )
            # save the highest timestamp from the fetched records for next run
            save_timestamp(
                settings.CONFIG["db_collection_projects"],
                data[next(iter(data))]["appealsEndDate"],
            )
    else:
        # fetch all records from the current-date time to process all records till now
        data = get_data_from_api(None)
        logging.info("Ordering data")
        data = OrderedDict(sorted(data.items(), key=lambda x: x[1]["appealsEndDate"], reverse=True))
        if data:
            logging.info("Data ordered %s", len(data))
            # save the highest timestamp from the fetched records for next run
            save_timestamp(
                settings.CONFIG["db_collection_projects"],
                data[next(iter(data))]["appealsEndDate"],
            )
            last_refreshed_at = datetime.strptime(
                list(data.values())[-1]["appealsEndDate"],
                "%Y-%m-%dT%H:%M:%S.%fZ",
            )

    logging.info("Data ordered %s", len(data))
    logging.info("Project Details Last Refreshed At - %s", last_refreshed_at)
    response = []
    if data:
        for project_id, project in data.items():
            project["project_id"] = project_id
            response.append(project)
        try:
            if response:
                # call the tagging tool on the filtered dataset only
                resp = get_tags(response, settings.TAGGING_CONFIG)
                if resp:
                    # saves the projects object along with extracted tags from tagging tool to DB
                    logging.info("Refreshing database with new win data")
                    save_project_details(resp)
                    return resp
                else:
                    save_timestamp(
                        settings.CONFIG["db_collection_projects"],
                        datetime.strftime(last_refreshed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
                    )
                    return []
        except Exception as e:
            logging.exception(str(e))
            save_timestamp(
                settings.CONFIG["db_collection_projects"],
                datetime.strftime(last_refreshed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            )
            return []


def run_tagging_tool_open():
    """pull data from API and tag them"""

    # fetch all records from the current-date time to process all records till now
    data = get_data_from_api_open()
    logging.info("Ordering data")
    data = OrderedDict(sorted(data.items(), key=lambda x: x[1]["startDate"], reverse=True))
    if data:
        logging.info("Data ordered %s", len(data))

    logging.info("Data ordered %s", len(data))
    response = []
    if data:
        for project_id, project in data.items():
            project["project_id"] = project_id
            response.append(project)
        try:
            if response:
                # call the tagging tool on the filtered dataset only
                resp = get_tags(response, settings.TAGGING_CONFIG)
                if resp:
                    # saves the projects object along with extracted tags from tagging tool to DB
                    logging.info("Refreshing database with new win data")
                    save_project_details(resp)
                    return resp
                else:
                    save_timestamp(
                        settings.CONFIG["db_collection_projects"],
                        datetime.strftime(last_refreshed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
                    )
                    return []
        except Exception as e:
            logging.exception(str(e))
            save_timestamp(
                settings.CONFIG["db_collection_projects"],
                datetime.strftime(last_refreshed_at, "%Y-%m-%dT%H:%M:%S.%fZ"),
            )
            return []
