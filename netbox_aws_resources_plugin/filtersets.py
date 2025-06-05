import django_filters
from django import forms
from ipam.models import Prefix
from netbox.filtersets import NetBoxModelFilterSet, TagFilter
from tenancy.filtersets import TenancyFilterSet
from utilities.filters import MultiValueCharFilter

from .models import (
    AWSAccount, AWSLoadBalancer, AWSSubnet, AWSVPC, AWSTargetGroup,
    AWS_REGION_CHOICES, TARGET_GROUP_PROTOCOL_CHOICES, TARGET_GROUP_TYPE_CHOICES, AWS_TARGET_GROUP_STATE_CHOICES
)


class AWSAccountFilterSet(NetBoxModelFilterSet, TenancyFilterSet):
    # Define filters for the AWSAccount model
    account_id = django_filters.CharFilter(lookup_expr="icontains", label="Account ID (contains)")
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name (contains)")
    parent_account = django_filters.ModelChoiceFilter(queryset=AWSAccount.objects.all(), label="Parent AWS Account")
    # tenant_id is inherited from TenancyFilterSet
    is_root_account = django_filters.BooleanFilter(
        method="filter_is_root_account",
        label="Is Root Account",
        widget=forms.Select(choices=[("", "Any"), ("true", "Yes"), ("false", "No")]),
    )

    class Meta:
        model = AWSAccount
        # Fields that can be filtered on. Add new fields here.
        # tenant_id comes from TenancyFilterSet
        fields = ["id", "account_id", "name", "parent_account", "is_root_account", "tag"]

    def filter_is_root_account(self, queryset, name, value):
        if value is True:
            return queryset.filter(parent_account__isnull=True)
        elif value is False:
            return queryset.filter(parent_account__isnull=False)
        return queryset


class AWSVPCFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name (contains)")
    vpc_id = django_filters.CharFilter(lookup_expr="icontains", label="VPC ID (contains)")
    aws_account_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AWSAccount.objects.all(), label="AWS Account (ID)"
    )
    region = django_filters.MultipleChoiceFilter(choices=AWSVPC._meta.get_field("region").choices, label="Region")
    cidr_block_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(), label="Primary CIDR Block (NetBox Prefix ID)"
    )
    cidr_block = django_filters.CharFilter(
        field_name="cidr_block__prefix", lookup_expr="icontains", label="Primary CIDR Block (e.g., 10.0.0.0/16)"
    )
    state = django_filters.MultipleChoiceFilter(choices=AWSVPC._meta.get_field("state").choices, label="State")
    is_default = django_filters.BooleanFilter(label="Is Default VPC")
    # tags will be inherited

    class Meta:
        model = AWSVPC
        fields = [
            "id",
            "name",
            "vpc_id",
            "aws_account_id",
            "region",
            "cidr_block_id",
            "cidr_block",
            "state",
            "is_default",
            "tag",
        ]


class AWSSubnetFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name (contains)")
    subnet_id = django_filters.CharFilter(lookup_expr="icontains", label="Subnet ID (contains)")
    aws_vpc_id = django_filters.ModelMultipleChoiceFilter(queryset=AWSVPC.objects.all(), label="AWS VPC (ID)")
    cidr_block_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Prefix.objects.all(), label="CIDR Block (NetBox Prefix ID)"
    )
    cidr_block = django_filters.CharFilter(
        field_name="cidr_block__prefix", lookup_expr="icontains", label="CIDR Block (e.g., 10.0.1.0/24)"
    )
    availability_zone = MultiValueCharFilter(label="Availability Zone (e.g., us-east-1a)")
    state = django_filters.MultipleChoiceFilter(choices=AWSSubnet._meta.get_field("state").choices, label="State")
    map_public_ip_on_launch = django_filters.BooleanFilter(label="Map Public IP on Launch")
    # tags will be inherited

    class Meta:
        model = AWSSubnet
        fields = [
            "id",
            "name",
            "subnet_id",
            "aws_vpc_id",
            "cidr_block_id",
            "cidr_block",
            "availability_zone",
            "state",
            "map_public_ip_on_launch",
            "tag",
        ]


class AWSLoadBalancerFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name (contains)")
    arn = django_filters.CharFilter(lookup_expr="icontains", label="ARN (contains)")
    aws_account_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AWSAccount.objects.all(), label="AWS Account (ID)"
    )
    # region = django_filters.MultipleChoiceFilter( # Region is now derived from VPC
    #     choices=AWSLoadBalancer._meta.get_field("region").choices,
    #     label="Region",
    # )
    vpc_id = django_filters.ModelMultipleChoiceFilter(queryset=AWSVPC.objects.all(), label="AWS VPC (ID)")
    type = django_filters.MultipleChoiceFilter(choices=AWSLoadBalancer._meta.get_field("type").choices, label="Type")
    scheme = django_filters.MultipleChoiceFilter(choices=AWSLoadBalancer._meta.get_field("scheme").choices, label="Scheme")
    state = django_filters.MultipleChoiceFilter(choices=AWSLoadBalancer._meta.get_field("state").choices, label="State")
    subnets = django_filters.ModelMultipleChoiceFilter(
        queryset=AWSSubnet.objects.all(),
        label="Subnets (ID)",
        # Conjunction=True, # Uncomment for AND logic (LB must be in ALL selected subnets)
    )
    tag = TagFilter()  # Explicitly define the tag filter (singular)

    class Meta:
        model = AWSLoadBalancer
        fields = ["id", "name", "arn", "aws_account_id", "vpc_id", "type", "scheme", "state", "subnets", "tag"]  # Changed 'tags' to 'tag'

# If you need to filter other models, define their FilterSets here


class AWSTargetGroupFilterSet(NetBoxModelFilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name (contains)")
    arn = django_filters.CharFilter(lookup_expr="icontains", label="ARN (contains)")
    aws_account_id = django_filters.ModelMultipleChoiceFilter(
        queryset=AWSAccount.objects.all(), label="AWS Account (ID)"
    )
    region = django_filters.MultipleChoiceFilter(choices=AWS_REGION_CHOICES, label="Region")
    vpc_id = django_filters.ModelMultipleChoiceFilter(queryset=AWSVPC.objects.all(), label="AWS VPC (ID)")
    protocol = django_filters.MultipleChoiceFilter(choices=TARGET_GROUP_PROTOCOL_CHOICES, label="Protocol")
    port = django_filters.NumberFilter(label="Port")
    target_type = django_filters.MultipleChoiceFilter(choices=TARGET_GROUP_TYPE_CHOICES, label="Target Type")
    state = django_filters.MultipleChoiceFilter(choices=AWS_TARGET_GROUP_STATE_CHOICES, label="State")
    load_balancers = django_filters.ModelMultipleChoiceFilter(
        queryset=AWSLoadBalancer.objects.all(),
        label="Load Balancers (ID)",
        field_name='load_balancers' # Explicitly specify field_name for M2M
    )
    tag = TagFilter()

    class Meta:
        model = AWSTargetGroup
        fields = [
            "id", "name", "arn", "aws_account_id", "region", "vpc_id",
            "protocol", "port", "target_type", "state", "load_balancers", "tag"
        ]
