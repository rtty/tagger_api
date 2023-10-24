import logging

from django.core.management.base import BaseCommand

from .tags.services.database_service import ProjectDetails

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create DynamoDB tables"

    def handle(self, *args, **kwargs):
        if not ProjectDetails.exists():
            ProjectDetails.create_table(read_capacity_units=1, write_capacity_units=1)

        logging.info(f"Table {ProjectDetails.Meta.table_name} created.")
