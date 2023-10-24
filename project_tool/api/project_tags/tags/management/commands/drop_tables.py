import logging

from django.core.management.base import BaseCommand

from tags.services.database_service import ProjectDetails

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Delete DynamoDB tables"

    def handle(self, *args, **kwargs):
        if ProjectDetails.exists():
            ProjectDetails.delete_table()

        logging.info(f"Table {ProjectDetails.Meta.table_name} deleted.")
