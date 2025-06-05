from django.urls import path
from netbox.views.generic import ObjectChangeLogView

from . import models, views

urlpatterns = [
    # AWS Accounts - List, Add, Individual View, Edit, Delete
    path("aws-accounts/", views.AWSAccountListView.as_view(), name="awsaccount_list"),
    path("aws-accounts/add/", views.AWSAccountEditView.as_view(), name="awsaccount_add"),
    path("aws-accounts/<int:pk>/", views.AWSAccountView.as_view(), name="awsaccount"),
    path("aws-accounts/<int:pk>/edit/", views.AWSAccountEditView.as_view(), name="awsaccount_edit"),
    path("aws-accounts/<int:pk>/delete/", views.AWSAccountDeleteView.as_view(), name="awsaccount_delete"),
    path(
        "aws-accounts/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awsaccount_changelog",
        kwargs={"model": models.AWSAccount},
    ),
    # AWS Accounts - Bulk Operations
    path("aws-accounts/edit/", views.AWSAccountBulkEditView.as_view(), name="awsaccount_bulk_edit"),
    path("aws-accounts/delete/", views.AWSAccountBulkDeleteView.as_view(), name="awsaccount_bulk_delete"),
    # If you add bulk import later:
    # path('aws-accounts/import/', views.AWSAccountBulkImportView.as_view(), name='awsaccount_import'),
    # AWS VPCs - List, Add, Individual View, Edit, Delete
    path("aws-vpcs/", views.AWSVPCListView.as_view(), name="awsvpc_list"),
    path("aws-vpcs/add/", views.AWSVPCEditView.as_view(), name="awsvpc_add"),
    path("aws-vpcs/<int:pk>/", views.AWSVPCView.as_view(), name="awsvpc"),
    path("aws-vpcs/<int:pk>/edit/", views.AWSVPCEditView.as_view(), name="awsvpc_edit"),
    path("aws-vpcs/<int:pk>/delete/", views.AWSVPCDeleteView.as_view(), name="awsvpc_delete"),
    path(
        "aws-vpcs/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awsvpc_changelog",
        kwargs={"model": models.AWSVPC},
    ),
    # AWS VPCs - Bulk Operations
    path("aws-vpcs/edit/", views.AWSVPCBulkEditView.as_view(), name="awsvpc_bulk_edit"),
    path("aws-vpcs/delete/", views.AWSVPCBulkDeleteView.as_view(), name="awsvpc_bulk_delete"),
    # If you add bulk import later for VPCs:
    # path('aws-vpcs/import/', views.AWSVPCBulkImportView.as_view(), name='awsvpc_import'),
    # AWS Subnets - List, Add, Individual View, Edit, Delete
    path("aws-subnets/", views.AWSSubnetListView.as_view(), name="awssubnet_list"),
    path("aws-subnets/add/", views.AWSSubnetEditView.as_view(), name="awssubnet_add"),
    path("aws-subnets/<int:pk>/", views.AWSSubnetView.as_view(), name="awssubnet"),
    path("aws-subnets/<int:pk>/edit/", views.AWSSubnetEditView.as_view(), name="awssubnet_edit"),
    path("aws-subnets/<int:pk>/delete/", views.AWSSubnetDeleteView.as_view(), name="awssubnet_delete"),
    path(
        "aws-subnets/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awssubnet_changelog",
        kwargs={"model": models.AWSSubnet},
    ),
    # AWS Subnets - Bulk Operations
    path("aws-subnets/edit/", views.AWSSubnetBulkEditView.as_view(), name="awssubnet_bulk_edit"),
    path("aws-subnets/delete/", views.AWSSubnetBulkDeleteView.as_view(), name="awssubnet_bulk_delete"),
    # If you add bulk import later for Subnets:
    # path('aws-subnets/import/', views.AWSSubnetBulkImportView.as_view(), name='awssubnet_import'),
    # AWS Load Balancers - List, Add, Individual View, Edit, Delete
    path("aws-load-balancers/", views.AWSLoadBalancerListView.as_view(), name="awsloadbalancer_list"),
    path("aws-load-balancers/add/", views.AWSLoadBalancerEditView.as_view(), name="awsloadbalancer_add"),
    path("aws-load-balancers/<int:pk>/", views.AWSLoadBalancerView.as_view(), name="awsloadbalancer"),
    path("aws-load-balancers/<int:pk>/edit/", views.AWSLoadBalancerEditView.as_view(), name="awsloadbalancer_edit"),
    path(
        "aws-load-balancers/<int:pk>/delete/", views.AWSLoadBalancerDeleteView.as_view(), name="awsloadbalancer_delete"
    ),
    path(
        "aws-load-balancers/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awsloadbalancer_changelog",
        kwargs={"model": models.AWSLoadBalancer},
    ),
    # AWS Load Balancers - Bulk Operations
    path("aws-load-balancers/edit/", views.AWSLoadBalancerBulkEditView.as_view(), name="awsloadbalancer_bulk_edit"),
    path(
        "aws-load-balancers/delete/", views.AWSLoadBalancerBulkDeleteView.as_view(), name="awsloadbalancer_bulk_delete"
    ),
    # If you add bulk import later for Load Balancers:
    # path('aws-load-balancers/import/', views.AWSLoadBalancerBulkImportView.as_view(), name='awsloadbalancer_import'),

    # AWS Target Groups - List, Add, Individual View, Edit, Delete
    path("aws-target-groups/", views.AWSTargetGroupListView.as_view(), name="awstargetgroup_list"),
    path("aws-target-groups/add/", views.AWSTargetGroupEditView.as_view(), name="awstargetgroup_add"),
    path("aws-target-groups/<int:pk>/", views.AWSTargetGroupView.as_view(), name="awstargetgroup"),
    path("aws-target-groups/<int:pk>/edit/", views.AWSTargetGroupEditView.as_view(), name="awstargetgroup_edit"),
    path("aws-target-groups/<int:pk>/delete/", views.AWSTargetGroupDeleteView.as_view(), name="awstargetgroup_delete"),
    path(
        "aws-target-groups/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="awstargetgroup_changelog",
        kwargs={"model": models.AWSTargetGroup},
    ),
    # AWS Target Groups - Bulk Operations
    path("aws-target-groups/edit/", views.AWSTargetGroupBulkEditView.as_view(), name="awstargetgroup_bulk_edit"),
    path("aws-target-groups/delete/", views.AWSTargetGroupBulkDeleteView.as_view(), name="awstargetgroup_bulk_delete"),
    # If you add bulk import later for Target Groups:
    # path('aws-target-groups/import/', views.AWSTargetGroupBulkImportView.as_view(), name='awstargetgroup_import'),
]
