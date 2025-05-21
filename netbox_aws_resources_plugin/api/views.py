from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets
from ..models import AWSVPC, AWSAccount, AWSSubnet

# The serializers.py is one level up from the 'api' directory
from .serializers import AWSAccountSerializer, AWSSubnetSerializer, AWSVPCSerializer


class AWSAccountViewSet(NetBoxModelViewSet):
    queryset = AWSAccount.objects.prefetch_related("tags")
    serializer_class = AWSAccountSerializer
    # If you have a specific filterset for the API, use it here, otherwise NetBoxModelViewSet provides some defaults
    # For consistency with the UI, let's use the same one:
    filterset_class = filtersets.AWSAccountFilterSet


class AWSVPCViewSet(NetBoxModelViewSet):
    queryset = AWSVPC.objects.prefetch_related("tags", "aws_account", "cidr_block")
    serializer_class = AWSVPCSerializer
    filterset_class = filtersets.AWSVPCFilterSet


class AWSSubnetViewSet(NetBoxModelViewSet):
    queryset = AWSSubnet.objects.prefetch_related("tags", "aws_vpc", "cidr_block")
    serializer_class = AWSSubnetSerializer
    filterset_class = filtersets.AWSSubnetFilterSet
