from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views


urlpatterns = (
    path("aws-resourcess/", views.AWSResourcesListView.as_view(), name="awsresources_list"),
    path("aws-resourcess/add/", views.AWSResourcesEditView.as_view(), name="awsresources_add"),
    path("aws-resourcess/<int:pk>/", views.AWSResourcesView.as_view(), name="awsresources"),
    path("aws-resourcess/<int:pk>/edit/", views.AWSResourcesEditView.as_view(), name="awsresources_edit"),
    path("aws-resourcess/<int:pk>/delete/", views.AWSResourcesDeleteView.as_view(), name="awsresources_delete"),
    path(
        "aws-resourcess/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awsresources_changelog",
        kwargs={"model": models.AWSResources},
    ),
)
