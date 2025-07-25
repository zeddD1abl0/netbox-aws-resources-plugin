from django import forms
from ipam.models import Prefix
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from utilities.forms.widgets import APISelect
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm

from ..models import AWSAccount, AWSVPC
from ..filtersets import AWSVPCFilterSet


class AWSVPCForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(), label="AWS Account", help_text="The AWS account this VPC belongs to"
    )
    cidr_block = DynamicModelChoiceField(
        label="CIDR Block (Prefix)",
        queryset=Prefix.objects.filter(
            prefix__isnull=True, is_pool=False, status="container"
        ),  # VPCs must be parent prefixes
        required=True,
        help_text="The NetBox Prefix representing the primary IPv4 CIDR of this VPC. Should be a container type.",
        query_params={"parent__isnull": "true", "status": "container"},
    )

    class Meta:
        model = AWSVPC
        fields = ("name", "vpc_id", "aws_account", "region", "cidr_block", "state", "is_default", "tags")
        widgets = {
            "aws_account": APISelect(attrs={"data-dynamic-parameters": "region_id"}),
            "cidr_block": APISelect(),
        }


class AWSVPCFilterForm(NetBoxModelFilterSetForm):
    model = AWSVPC
    filterset = AWSVPCFilterSet

    vpc_id = forms.CharField(required=False, label="VPC ID")
    name = forms.CharField(required=False)
    aws_account_id = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSVPC._meta.get_field("region").choices), required=False
    )
    state = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSVPC._meta.get_field("state").choices), required=False
    )
    is_default = forms.NullBooleanField(
        required=False,
        label="Is Default VPC",
        widget=forms.Select(choices=[("", "Any"), ("true", "Yes"), ("false", "No")]),
    )
    tag = TagFilterField(model)


class AWSVPCBulkEditForm(NetBoxModelBulkEditForm):
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSVPC._meta.get_field("region").choices), required=False
    )
    state = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSVPC._meta.get_field("state").choices), required=False
    )
    is_default = forms.NullBooleanField(
        required=False,
        label="Is Default VPC",
        widget=forms.Select(choices=[("", "Any"), ("true", "Yes"), ("false", "No")]),
    )

    model = AWSVPC
    nullable_fields = ("name", "aws_account", "region", "cidr_block", "state", "is_default")
