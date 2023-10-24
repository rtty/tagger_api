import logging

from django.core.management.base import BaseCommand

from tags.services.database_service import ProjectDetails

# Get an instance of a logger
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "View DynamoDB tables"

    # allows for command line args
    def add_arguments(self, parser):
        parser.add_argument("table", type=str, help="Table name")
        parser.add_argument("-i", "--id", type=str, help="Record Id")

    def handle(self, *args, **kwargs):
        table = kwargs.get("table")
        id = kwargs.get("id")

        if table == ProjectDetails.Meta.table_name:
            if id:
                result = ProjectDetails.query(id)
            else:
                result = ProjectDetails.scan()

            for rec in result:
                output_tag = []
                if rec.output_tag:
                    for t in rec.output_tag:
                        output_tag.append({"tag": t.tag, "type": t.type, "source": t.source})

                winners = []
                if rec.winners:
                    for w in rec.winners:
                        winners.append({"handle": w.handle, "placement": w.placement})

                out = {"_id": rec._id}
                if rec.name:
                    out["name"] = rec.name
                if rec.startDate:
                    out["startDate"] = rec.startDate
                if rec.endDate:
                    out["endDate"] = rec.endDate
                if rec.track:
                    out["track"] = rec.track
                if rec.LastRefreshedAt:
                    out["LastRefreshedAt"] = rec.LastRefreshedAt
                if rec.appealsEndDate:
                    out["appealsEndDate"] = rec.appealsEndDate
                if len(output_tag) > 0:
                    out["output_tag"] = output_tag
                if len(winners) > 0:
                    out["winners"] = winners

                logging.info(out)
        else:
            logging.info(f"Invalid table {table}.")
