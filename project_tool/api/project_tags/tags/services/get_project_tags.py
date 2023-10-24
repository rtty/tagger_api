import logging

from pynamodb.exceptions import DoesNotExist
from rest_framework.exceptions import NotFound

from ..exceptions.exceptions import BadRequest
from ..serializers.serializers import (
    ProjectDetailsSerializer,
    ProjectTagsSerializer,
)
from .database_service import get_project_tags
from .raw_tagging_service import get_projects_open

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_project_tags_service(request):
    try:
        project_id = request.GET.get("project_id", "")
        output_tag = request.GET.get("output_tag", False)

        projects_from_db = []
        if not project_id:
            status = request.GET.get("status", "").lower()
            if status == "open":  # get all open projects
                open_projects = get_projects_open(dict(request.GET))
                for project in open_projects:
                    response = get_project_tags(project["id"])
                    if not isinstance(response, DoesNotExist) and not isinstance(response, str):
                        temp = [
                            tag.tag
                            for tag in response.output_tag
                            if response.output_tag is not None
                        ]
                        project["output_tag"] = temp
                        projects_from_db.append(project)
            else:  # get all projects
                projects_from_db = get_project_tags(None)
            if isinstance(
                projects_from_db, DoesNotExist
            ):  # projects not found in the database, empty database
                raise NotFound("message: Projects not found in the database.")
        else:
            project_id = project_id.split(",")
            for project in project_id:
                project = project.strip()  # remove whitespaces if there are any
                response = get_project_tags(project)
                if not isinstance(response, DoesNotExist) and not isinstance(response, str):
                    projects_from_db.append(response)

        if not project_id and status == "open":
            result = projects_from_db
        elif output_tag:
            result = [
                ProjectTagsSerializer(i).data for i in projects_from_db if i.output_tag is not None
            ]
        else:
            result = [
                ProjectDetailsSerializer(i).data
                for i in projects_from_db
                if i.output_tag is not None
            ]

        # if parameter 'tag' is set in the request keep only projects that have this tag(s)
        # endpoint accepts multiple, comma separated tags
        tag = request.GET.get("tag", None)
        if tag:
            tags = tag.split(",")
            logging.debug("Get projects with only these tags: {}".format(tags))
            temp = []
            for project in result:
                if all(tag in project["output_tag"] for tag in tags):
                    temp.append(project)
            result = temp

        return result
    except Exception as e:
        logger.exception(str(e))
        raise BadRequest({"message": str(e)})
