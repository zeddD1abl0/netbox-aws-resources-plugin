from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from tenancy.models import Tenant
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from utilities.forms.widgets import APISelect

from .filtersets import AWSAccountFilterSet, AWSLoadBalancerFilterSet, AWSSubnetFilterSet, AWSVPCFilterSet
from .models import AWSVPC, AWSAccount, AWSLoadBalancer, AWSSubnet


class AWSAccountForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    parent_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
        label="Parent AWS Account",
    )

    class Meta:
        model = AWSAccount
        fields = ("account_id", "name", "tenant", "parent_account", "tags")


class AWSAccountFilterForm(NetBoxModelFilterSetForm):
    model = AWSAccount
    filterset = AWSAccountFilterSet
    account_id = forms.CharField(required=False, label="Account ID")
    name = forms.CharField(required=False)
    tenant_id = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False, label="Tenant")
    parent_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(), required=False, label="Parent AWS Account"
    )
    is_root_account = forms.NullBooleanField(
        required=False,
        label="Is Root Account",
    )
    tag = TagFilterField(model)


class AWSAccountBulkEditForm(NetBoxModelBulkEditForm):
    name = forms.CharField(required=False, label="Name")
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    parent_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(), required=False, label="Parent AWS Account"
    )

    model = AWSAccount
    nullable_fields = ("name", "tenant", "parent_account")


# Forms for AWSVPC


class AWSVPCForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(), label="AWS Account", help_text="The AWS account this VPC belongs to"
    )
    cidr_block = DynamicModelChoiceField(
        label="CIDR Block (Prefix)",
        queryset=Prefix.objects.filter(is_pool=False, status="container"),  # Typically VPCs are container prefixes
        required=False,  # Depending on workflow, might be set later or not at all initially
        help_text="The NetBox Prefix representing the primary IPv4 CIDR of this VPC. Should be a container type.",
    )

    class Meta:
        model = AWSVPC
        fields = ("name", "vpc_id", "aws_account", "region", "cidr_block", "state", "is_default", "tags")
        widgets = {
            "aws_account": APISelect(attrs={"data-dynamic-parameters": "region_id"}),
            "cidr_block": APISelect(),
            # 'state': APISelect(), # Removed to use default widget for choices
        }


class AWSVPCFilterForm(NetBoxModelFilterSetForm):
    model = AWSVPC
    filterset = AWSVPCFilterSet  # This will need to be created in filtersets.py

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
    # Consider adding filter for cidr_block (e.g., by its string representation or Prefix ID)
    tag = TagFilterField(model)


class AWSVPCBulkEditForm(NetBoxModelBulkEditForm):
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSVPC._meta.get_field("region").choices), required=False
    )
    # cidr_block is tricky for bulk edit, typically not changed in bulk for existing VPCs.
    # If needed, one might allow setting it if null, or clearing it.
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


# Forms for AWSSubnet


class AWSSubnetForm(NetBoxModelForm):
    aws_vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(), label="AWS VPC", help_text="The AWS VPC this subnet belongs to"
    )
    # Hidden fields to store details from the selected VPC for filtering
    _vpc_cidr_for_filter = forms.CharField(required=False, widget=forms.HiddenInput())
    _vpc_vrf_id_for_filter = forms.CharField(
        required=False, widget=forms.HiddenInput()  # VRF ID might be null if global
    )

    cidr_block = DynamicModelChoiceField(
        label="CIDR Block (Prefix)",
        queryset=Prefix.objects.none(),  # Initially empty
        help_text="The NetBox Prefix representing the IPv4 CIDR of this subnet. Must be a child prefix of the VPC.",
        query_params={"within": "$_vpc_cidr_for_filter", "vrf_id": "$_vpc_vrf_id_for_filter"},
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
            # DO NOT include _vpc_cidr_for_filter or _vpc_vrf_id_for_filter here
        )
        widgets = {
            "aws_vpc": APISelect(),
            "cidr_block": APISelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        selected_vpc = None
        if self.is_bound and self.data.get("aws_vpc"):
            try:
                selected_vpc = AWSVPC.objects.filter(
                    pk=self.data.get("aws_vpc")
                ).first()  # Use filter().first() to avoid DoesNotExist
            except ValueError:  # Handle non-integer PK
                pass
        elif self.instance and self.instance.pk and self.instance.aws_vpc:
            selected_vpc = self.instance.aws_vpc

        if selected_vpc and selected_vpc.cidr_block:
            # This queryset is for initial load/server-side validation context
            self.fields["cidr_block"].queryset = Prefix.objects.filter(
                prefix__net_contained=selected_vpc.cidr_block.prefix, vrf=selected_vpc.cidr_block.vrf, is_pool=False
            )
        else:
            self.fields["cidr_block"].queryset = Prefix.objects.none()

    # Include JS for populating hidden fields
    class Media:
        js = ("netbox_aws_resources_plugin/js/subnet_form.js",)


class AWSSubnetFilterForm(NetBoxModelFilterSetForm):
    model = AWSSubnet
    filterset = AWSSubnetFilterSet  # This will need to be created in filtersets.py

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
        choices=add_blank_choice(AWSSubnet._meta.get_field("state").choices), required=False, label="State"
    )
    map_public_ip_on_launch = forms.NullBooleanField(
        required=False, label="Map Public IP on Launch", widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES)
    )

    model = AWSSubnet
    nullable_fields = ["aws_vpc", "availability_zone", "state", "map_public_ip_on_launch", "description", "comments"]


# Forms for AWSLoadBalancer


class AWSLoadBalancerForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        label="AWS Account",
        help_text="The AWS account this Load Balancer belongs to",
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        label="AWS VPC",
        required=False,
        help_text="The AWS VPC this Load Balancer is associated with (optional)",
        query_params={"aws_account_id": "$aws_account"},
    )
    # Region, Type, Scheme, State will use default dropdowns based on model choices

    class Meta:
        model = AWSLoadBalancer
        fields = ("name", "arn", "aws_account", "region", "vpc", "type", "scheme", "dns_name", "state", "tags")
        widgets = {
            "aws_account": APISelect(attrs={"data-dynamic-parameters": "region_id"}),
            "region": APISelect(),
            "vpc": APISelect(),
            "type": APISelect(),
            "scheme": APISelect(),
            "state": APISelect(),
        }


class AWSLoadBalancerFilterForm(NetBoxModelFilterSetForm):
    model = AWSLoadBalancer
    filterset = AWSLoadBalancerFilterSet

    name = forms.CharField(required=False)
    arn = forms.CharField(required=False, label="ARN")
    aws_account_id = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("region").choices), required=False
    )
    vpc_id = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="AWS VPC")
    type = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("type").choices), required=False
    )
    scheme = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("scheme").choices), required=False
    )
    state = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("state").choices), required=False
    )
    tag = TagFilterField(model)


class AWSLoadBalancerBulkEditForm(NetBoxModelBulkEditForm):
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("region").choices), required=False
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
        label="AWS VPC",
        # If VPCs should be filtered by a potentially bulk-edited account, that's more complex.
        # For now, allowing selection from all VPCs or clearing.
    )
    type = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("type").choices), required=False
    )
    scheme = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("scheme").choices), required=False
    )
    state = forms.ChoiceField(
        choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("state").choices), required=False
    )

    model = AWSLoadBalancer
    nullable_fields = ["aws_account", "region", "vpc", "type", "scheme", "state", "description", "comments"]
