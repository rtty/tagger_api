from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ProjectPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 100

    def get_paginated_response(self, data):
        # API Requirements
        headers = {
            "X-Next-Page": self.page.next_page_number()
            if self.page.has_next()
            else self.page.end_index(),
            "X-Page": self.page.number,
            "X-Per-Page": self.page.paginator.per_page,
            "X-Perv-Page": self.page.previous_page_number()
            if self.page.has_previous()
            else self.page.start_index(),
            "X-Total": self.page.paginator.count,
            "X-Total-Pages": self.page.paginator.num_pages,
        }
        return Response(data, headers=headers)
