from netbox.api.routers import NetBoxRouter

from . import views

app_name = "netbox_aws_resources_plugin-api"  # Or choose a different app_name if you prefer

router = NetBoxRouter()
router.register("aws-accounts", views.AWSAccountViewSet)
router.register("aws-vpcs", views.AWSVPCViewSet)
router.register("aws-subnets", views.AWSSubnetViewSet)
router.register("aws-load-balancers", views.AWSLoadBalancerViewSet)
router.register("aws-target-groups", views.AWSTargetGroupViewSet)

urlpatterns = router.urls
