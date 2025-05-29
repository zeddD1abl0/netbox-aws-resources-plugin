from django import forms
from ipam.models import Prefix
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.widgets import APISelect
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm

from ..models import AWSVPC, AWSSubnet
from ..filtersets import AWSSubnetFilterSet


class AWSSubnetForm(NetBoxModelForm):
    aws_vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(), label="AWS VPC", help_text="The AWS VPC this subnet belongs to"
    )
    # Hidden fields to store details from the selected VPC for filtering
    _vpc_cidr_for_filter = forms.CharField(required=False, widget=forms.HiddenInput())
    _vpc_vrf_id_for_filter = forms.CharField(
        required=False, widget=forms.HiddenInput() 
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
                ).first()
            except ValueError:
                pass
        elif self.instance and self.instance.pk and self.instance.aws_vpc:
            selected_vpc = self.instance.aws_vpc

        if selected_vpc and selected_vpc.cidr_block:
            self.fields["cidr_block"].queryset = Prefix.objects.filter(
                prefix__net_contained_or_equal=selected_vpc.cidr_block.prefix,
                vrf=selected_vpc.cidr_block.vrf, 
                is_pool=False
            ).exclude(pk=selected_vpc.cidr_block.pk) 
            # Populate hidden fields for JS if VPC is already selected
            if not self.is_bound: # Only set initial if not bound, to avoid overwriting user input
                self.initial['_vpc_cidr_for_filter'] = str(selected_vpc.cidr_block.prefix)
                if selected_vpc.cidr_block.vrf:
                    self.initial['_vpc_vrf_id_for_filter'] = str(selected_vpc.cidr_block.vrf.pk)
                else:
                    self.initial['_vpc_vrf_id_for_filter'] = ''
        else:
            self.fields["cidr_block"].queryset = Prefix.objects.none()

    class Media:
        js = ("netbox_aws_resources_plugin/js/subnet_form.js",)


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
        choices=add_blank_choice(AWSSubnet._meta.get_field('state').choices),
        required=False,
        initial=''
    )
    map_public_ip_on_launch = forms.NullBooleanField(
        required=False,
        widget=forms.Select(choices=BOOLEAN_WITH_BLANK_CHOICES)
    )

    model = AWSSubnet
    nullable_fields = ('aws_vpc', 'availability_zone', 'state', 'map_public_ip_on_launch')
