import logging
from datetime import datetime

from django.conf import settings
from pynamodb.attributes import ListAttribute, MapAttribute, UnicodeAttribute
from pynamodb.exceptions import DoesNotExist
from pynamodb.models import Model

# Get an instance of a logger
logger = logging.getLogger(__name__)


class TagAttribute(MapAttribute):
    """Tag Attribute"""

    tag = UnicodeAttribute(null=True)
    type = UnicodeAttribute(null=True)
    source = UnicodeAttribute(null=True)


class WinnerAttribute(MapAttribute):
    """Winner Attribute"""

    handle = UnicodeAttribute(null=True)
    placement = UnicodeAttribute(null=True)
    userId = UnicodeAttribute(null=True)


class ProjectDetails(Model):
    """DynamoDB Project Details"""

    class Meta:
        table_name = settings.CONFIG["db_collection_projects"]
        host = settings.CONFIG["aws_dynamodb_url"]
        region = settings.CONFIG["aws_default_region"]

    name = UnicodeAttribute(null=True)
    _id = UnicodeAttribute(hash_key=True)

    startDate = UnicodeAttribute(null=True)
    endDate = UnicodeAttribute(null=True)
    track = UnicodeAttribute(null=True)
    LastRefreshedAt = UnicodeAttribute(null=True)
    appealsEndDate = UnicodeAttribute(null=True)
    output_tag = ListAttribute(of=TagAttribute, null=True)
    winners = ListAttribute(of=WinnerAttribute, null=True)


def save_project_details(response):
    """Saves the project details to DB"""
    count = 0
    for res in response:
        if "winners" in res and res["winners"]:
            res["winners"] = [update_dict_array(x) for x in res["winners"]]
        item = ProjectDetails(res["_id"])
        item.name = res["name"]
        item.startDate = res["startDate"]
        item.endDate = res["endDate"] if "endDate" in res else None
        item.track = res["track"]
        item.appealsEndDate = res["appealsEndDate"] if "appealsEndDate" in res else None
        item.output_tag = res["output_tag"]
        item.winners = res["winners"] if "winners" in res else None
        item.save()
        count += 1

    logging.info("Db Updated - %s", count)


def update_dict_array(dictionary):
    for key in dictionary.keys():
        update_dict(dictionary, key)
    return dictionary


def update_dict(dictionary, key):
    up = {key: str(dictionary[key])}
    dictionary.update(up)


def get_last_refreshed_at(collection_name):
    """Returns the LastRefreshedAt details From DB"""
    try:
        if collection_name == ProjectDetails.Meta.table_name:
            item = ProjectDetails.get("1")
    except:
        item = None
    if item:
        return datetime.strptime(item.LastRefreshedAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        return None


def save_timestamp(collection_name, refresh_time):
    """Updates the LastRefreshedAt details to DB default is current datetime"""
    if collection_name == ProjectDetails.Meta.table_name:
        item = ProjectDetails("1")
        item.LastRefreshedAt = refresh_time
        item.save()


def get_project_tags(project_id):
    """
    Returns the project tags for a given project id or all tags for all projects
    :param project_id: id of a project to get from the database,
            if project_id is None -> get all projects from the database
    :return: a list of a tags
            or if project_id is None a dictionary with projects as keys and for given key a list of tags
    """

    if project_id:
        try:
            records = ProjectDetails.get(project_id)
        except DoesNotExist as e:
            return e
        except:
            records = None
        return records

    else:  # get all projects from the database
        try:
            records = ProjectDetails.scan()
        except:
            records = None
        return records
