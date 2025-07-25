import json
import os
from django import forms
from ipam.models import Prefix
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.widgets import APISelect
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm

from ..models import AWSVPC, AWSSubnet
from ..filtersets import AWSSubnetFilterSet

# Load AZ data from JSON file
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "az_data.json")
with open(file_path) as f:
    AZ_DATA = json.load(f)


# Create a flattened, unique, sorted list of all possible AZs
all_azs = sorted(list(set(az for region_azs in AZ_DATA.values() for az in region_azs)))
AZ_CHOICES = [(az, az) for az in all_azs]


class AWSSubnetForm(NetBoxModelForm):
    aws_vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(), label="AWS VPC", help_text="The AWS VPC this subnet belongs to"
    )
    cidr_block = DynamicModelChoiceField(
        label="CIDR Block (Prefix)",
        queryset=Prefix.objects.select_related("aws_vpc_primary_cidr"),
        help_text="The NetBox Prefix representing the IPv4 CIDR of this subnet.",
    )
    availability_zone = forms.ChoiceField(
        choices=add_blank_choice(AZ_CHOICES), required=False, label="Availability Zone"
    )

    class Meta:
        model = AWSSubnet
        fields = (
            "name",
            "subnet_id",
            "aws_vpc",
            "cidr_block",
            "availability_zone",
            "state",
            "map_public_ip_on_launch",
            "tags",
        )
        widgets = {
            "aws_vpc": APISelect(),
            "cidr_block": APISelect(),
        }


class AWSSubnetFilterForm(NetBoxModelFilterSetForm):
    model = AWSSubnet
    filterset = AWSSubnetFilterSet

    subnet_id = forms.CharField(required=False, label="Subnet ID")
    name = forms.CharField(required=False)
    aws_vpc_id = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="AWS VPC")
    map_public_ip_on_launch = forms.NullBooleanField(
        required=False,
        label="Map Public IP on Launch",
        widget=forms.Select(choices=[("", "Any"), ("true", "Yes"), ("false", "No")]),
    )


class AWSSubnetBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=AWSSubnet.objects.all(), widget=forms.MultipleHiddenInput)
    aws_vpc = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="AWS VPC")
    availability_zone = forms.CharField(required=False, label="Availability Zone")
    state = forms.ChoiceField(
        choices=add_blank_choice(AWSSubnet._meta.get_field("state").choices), required=False, initial=""
    )
    map_public_ip_on_launch = forms.NullBooleanField(
        required=False, widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES)
    )

    model = AWSSubnet
    nullable_fields = ("aws_vpc", "availability_zone", "state", "map_public_ip_on_launch")
