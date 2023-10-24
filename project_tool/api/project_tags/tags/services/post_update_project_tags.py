import asyncio

from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from ..exceptions.exceptions import BadRequest, DatabaseError
from .asynchronous_service import asyn_update_project_tag
from .raw_tagging_service import *

# Get an instance of a logger
logger = logging.getLogger(__name__)


def update_project_tag_service(request):
    try:
        run_async = request.query_params.get("async", "false").lower()
        # validate input
        true_or_false = ("true", "false")
        if run_async not in true_or_false:
            raise ValidationError(
                message="Invalid input async: {}. Possible values: {}".format(
                    run_async, true_or_false
                )
            )
        result = {}

        if run_async == "true":
            asyncio.ensure_future(
                asyn_update_project_tag(
                    "skills.notification.update",
                    "update_project_tag",
                    update_project_tag,
                )
            )
            loop = asyncio.get_event_loop()
            loop.create_task(
                asyn_update_project_tag(
                    "skills.notification.update",
                    "update_project_tag",
                    update_project_tag,
                )
            )
        else:
            result = update_project_tag()

        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(str(e))
        raise BadRequest({"message": str(e)})


def update_project_tag_service_open(request):
    try:
        run_async = request.query_params.get("async", "false").lower()
        # validate input
        true_or_false = ("true", "false")
        if run_async not in true_or_false:
            raise ValidationError(
                message="Invalid input async: {}. Possible values: {}".format(
                    run_async, true_or_false
                )
            )
        result = {}

        if run_async == "true":
            asyncio.ensure_future(
                asyn_update_project_tag(
                    "skills.notification.update",
                    "update_project_tag",
                    update_project_tag_open,
                )
            )
            loop = asyncio.get_event_loop()
            loop.create_task(
                asyn_update_project_tag(
                    "skills.notification.update",
                    "update_project_tag",
                    update_project_tag_open,
                )
            )
        else:
            result = update_project_tag_open()

        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(str(e))
        raise BadRequest({"message": str(e)})


def update_project_tag():
    """Part of the post function that can be run synchronously or synchronously"""

    resp = run_tagging_tool()
    if resp:
        # saves the projects object along with extracted tags from tagging tool to DB
        logging.info("Refreshing database with new win data")
        try:
            save_project_details(resp)
        except Exception as e:
            logger.exception(str(e))
            raise DatabaseError(e)

    result = {"Projects Updated": len(resp) if resp else 0, "result": resp}
    return result


def update_project_tag_open():
    """Part of the post function that can be run synchronously or synchronously"""

    resp = run_tagging_tool_open()
    if resp:
        # saves the projects object along with extracted tags from tagging tool to DB
        logging.info("Refreshing database with new win data")
        try:
            save_project_details(resp)
        except Exception as e:
            logger.exception(str(e))
            raise DatabaseError(e)

    result = {"Projects Updated": len(resp) if resp else 0, "result": resp}
    return result
