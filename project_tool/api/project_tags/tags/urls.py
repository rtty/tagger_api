from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views

urlpatterns = [
    path("/health", views.GetHealthView.as_view(), name="health"),
    path(
        "/tags",
        views.UpdateProjectTagsView.as_view(),
        name="update_project_tags",
    ),
    path(
        "/completed",
        views.UpdateCompletedProjectTagsView.as_view(),
        name="update_completed_project_tags",
    ),
    path(
        "/open",
        views.UpdateOpenProjectTagsView.as_view(),
        name="update_open_project_tags",
    ),
    path("", views.GetProjectTagsView.as_view(), name="project_tags"),
    path("/api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "/api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

urlpatterns += staticfiles_urlpatterns()
