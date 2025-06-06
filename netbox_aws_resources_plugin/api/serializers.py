from ipam.api.serializers import (
    NestedPrefixSerializer as NetBoxNestedPrefixSerializer,
)  # Use NetBox's nested Prefix serializer
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer
from rest_framework import serializers
from tenancy.api.serializers import TenantSerializer  # Assuming you might use this for tenant

from ..models import AWSVPC, AWSAccount, AWSSubnet, AWSLoadBalancer, AWSTargetGroup


# Nested serializer for representing parent_account concisely
class NestedAWSAccountSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aws_resources_plugin-api:awsaccount-detail"
    )

    class Meta:
        model = AWSAccount
        fields = ("id", "url", "account_id", "name")  # Key fields for nested display


class NestedTenantSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="tenancy-api:tenant-detail")

    class Meta:
        model = TenantSerializer.Meta.model
        fields = ("id", "url", "name", "slug", "display")


# Main serializer for AWSAccount
class AWSAccountSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="plugins-api:netbox_aws_resources_plugin-api:awsaccount-detail"
    )
    tenant = NestedTenantSerializer(required=False, allow_null=True)
    parent_account = NestedAWSAccountSerializer(  # Added parent_account
        # queryset=AWSAccount.objects.all(), # Removed queryset argument
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AWSAccount
        fields = (
            "id",
            "url",
            "display",
            "account_id",
            "name",
            "tenant",
            "parent_account",  # Added parent_account
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "account_id", "name")


# Serializers for AWSVPC


class NestedAWSVPCSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awsvpc-detail")

    class Meta:
        model = AWSVPC
        fields = ("id", "url", "display", "vpc_id", "name")


class AWSVPCSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awsvpc-detail")
    aws_account = NestedAWSAccountSerializer(read_only=True)  # Or queryset if writable is needed
    cidr_block = NetBoxNestedPrefixSerializer(read_only=True)  # Use NetBox's nested Prefix serializer
    # For writable nested fields, you would typically provide a queryset and remove read_only=True
    # Example for aws_account if it were writable:
    # aws_account = NestedAWSAccountSerializer(queryset=AWSAccount.objects.all())
    # Example for cidr_block if it were writable and custom:
    # cidr_block = NestedPrefixSerializer(queryset=Prefix.objects.all())

    class Meta:
        model = AWSVPC
        fields = (
            "id",
            "url",
            "display",
            "name",
            "vpc_id",
            "aws_account",
            "region",
            "cidr_block",
            "state",
            "is_default",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "vpc_id", "name", "region")


# Serializers for AWSSubnet


class NestedAWSSubnetSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awssubnet-detail")

    class Meta:
        model = AWSSubnet
        fields = ("id", "url", "display", "subnet_id", "name")


class AWSSubnetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awssubnet-detail")
    aws_vpc = NestedAWSVPCSerializer(read_only=True)  # Or queryset if writable
    cidr_block = NetBoxNestedPrefixSerializer(read_only=True)  # Or queryset if writable

    class Meta:
        model = AWSSubnet
        fields = (
            "id",
            "url",
            "display",
            "name",
            "subnet_id",
            "aws_vpc",
            "cidr_block",
            "availability_zone",
            "state",
            "map_public_ip_on_launch",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "subnet_id", "name", "availability_zone")


# Serializers for AWSLoadBalancer (Placeholder if not already present)
class NestedAWSLoadBalancerSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awsloadbalancer-detail")

    class Meta:
        model = AWSLoadBalancer
        fields = ("id", "url", "display", "name", "arn")

class AWSLoadBalancerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awsloadbalancer-detail")
    aws_account = NestedAWSAccountSerializer(read_only=True)
    vpc = NestedAWSVPCSerializer(read_only=True, required=False, allow_null=True)
    subnets = NestedAWSSubnetSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = AWSLoadBalancer
        fields = (
            "id",
            "url",
            "display",
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "type",
            "scheme",
            "dns_name",
            "state",
            "subnets",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "arn", "region", "type")


# Serializers for AWSTargetGroup
class NestedAWSTargetGroupSerializer(WritableNestedSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awstargetgroup-detail")

    class Meta:
        model = AWSTargetGroup
        fields = ("id", "url", "display", "name", "arn")


class AWSTargetGroupSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_aws_resources_plugin-api:awstargetgroup-detail")
    aws_account = NestedAWSAccountSerializer(read_only=True)
    vpc = NestedAWSVPCSerializer(read_only=True, required=False, allow_null=True)
    load_balancers = NestedAWSLoadBalancerSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = AWSTargetGroup
        fields = (
            "id",
            "url",
            "display",
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "protocol",
            "port",
            "target_type",
            "load_balancers",
            "health_check_protocol",
            "health_check_port",
            "health_check_path",
            "health_check_interval_seconds",
            "health_check_timeout_seconds",
            "healthy_threshold_count",
            "unhealthy_threshold_count",
            "state",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "arn", "region", "protocol", "port", "target_type")
