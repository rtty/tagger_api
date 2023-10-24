from rest_framework import status
from rest_framework.response import Response

from ..exceptions.exceptions import BadRequest, DatabaseError
from .raw_tagging_service import *

logger = logging.getLogger(__name__)


def update_project_tags_service(request):
    logging.info(request.data)
    project_ids = request.data.get("projectId", "")

    if not project_ids:
        raise BadRequest("projectId is missing from the body")
    else:
        logging.info(request.data)
        projects_to_create_or_update = []
        for project_id in project_ids:
            project_id = project_id.strip()  # remove whitespaces if there are any
            project = get_single_project(project_id)
            if project:
                project["project_id"] = project_id
                projects_to_create_or_update.append(project)
        resp = get_tags(projects_to_create_or_update, settings.TAGGING_CONFIG)
        if resp:
            # saves the projects object along with extracted tags from tagging tool to DB
            logging.info("Refreshing database with new win data")
            try:
                save_project_details(resp)
            except Exception as e:
                logging.exception(str(e))
                raise DatabaseError(e)
        return Response({"Projects Updated": len(resp)}, status=status.HTTP_200_OK)
