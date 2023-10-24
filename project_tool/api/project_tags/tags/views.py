from asgiref.sync import async_to_sync
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from project_tags.jwt_authenticator import M2MAuthentication
from project_tags.pagination import ProjectPagination

from .serializers.serializers import ProjectDetailsSerializer
from .services.get_project_tags import get_project_tags_service
from .services.post_update_project_tags import *
from .services.update_project_tags import *

# Create your views here.


class GetHealthView(APIView):
    def get(self, request):
        response = {"data": {"message": "Service is healthy", "healthy": True}}
        return Response(response, status=status.HTTP_200_OK)


class UpdateProjectTagsView(APIView):
    """Contains logic to update project tags based on project ids"""

    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]
    authentication_classes = [M2MAuthentication]

    @extend_schema(
        parameters=[OpenApiParameter(name="project_ids", type=str, location=OpenApiParameter.QUERY)]
    )
    @async_to_sync
    async def put(self, request):
        return update_project_tags_service(request)


class UpdateCompletedProjectTagsView(APIView):
    """Contains logic to update project tags for all completed projects"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [M2MAuthentication]

    @extend_schema(
        parameters=[OpenApiParameter(name="async", type=bool, location=OpenApiParameter.QUERY)],
    )
    @async_to_sync
    async def put(self, request):
        return update_project_tag_service(request)


class UpdateOpenProjectTagsView(APIView):
    """Contains logic to update project tags for all open projects"""

    permission_classes = [IsAuthenticated]
    authentication_classes = [M2MAuthentication]

    @extend_schema(
        parameters=[OpenApiParameter(name="async", type=bool, location=OpenApiParameter.QUERY)],
    )
    @async_to_sync
    async def put(self, request):
        return update_project_tag_service_open(request)


class GetProjectTagsView(GenericAPIView):
    pagination_class = ProjectPagination
    serializer_class = ProjectDetailsSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="project_id",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(name="page", type=int, location=OpenApiParameter.QUERY),
            OpenApiParameter(name="per_page", type=int, location=OpenApiParameter.QUERY),
            OpenApiParameter(
                name="tag",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
            OpenApiParameter(
                name="output_tag",
                type=bool,
                location=OpenApiParameter.QUERY,
                required=False,
            ),
        ],
        responses=ProjectDetailsSerializer,
    )
    def get(self, request):
        return self.get_paginated_response(
            self.paginate_queryset(get_project_tags_service(request))
        )
