from django import forms
# from ipam.models import Prefix # Uncomment if needed for LB forms
# from tenancy.models import Tenant # Uncomment if needed for LB forms
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES, add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField, DynamicModelMultipleChoiceField
from utilities.forms.widgets import APISelect, APISelectMultiple
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm

from ..models import AWSAccount, AWSVPC, AWSSubnet, AWSLoadBalancer
from ..filtersets import AWSLoadBalancerFilterSet


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
        query_params={"aws_account_id": "$aws_account"}, # Filters VPCs by selected account
    )
    subnets = DynamicModelMultipleChoiceField(
        queryset=AWSSubnet.objects.all(), # Initial queryset, will be overridden by __init__ and JS
        required=False,
        label="Associated Subnets",
        help_text="Subnets to associate with this Load Balancer. Should be within the selected VPC.",
        query_params={"aws_vpc_id": "$vpc"} # JS should use this to filter and manage enabled/disabled state
    )
    # Region, Type, Scheme, State will use default dropdowns based on model choices

    class Meta:
        model = AWSLoadBalancer
        fields = ("name", "arn", "aws_account", "vpc", "subnets", "type", "scheme", "dns_name", "state", "tags")
        widgets = {
            "aws_account": APISelect(attrs={"data-dynamic-parameters": "region_id"}),
            # vpc field uses default widget from DynamicModelChoiceField (APISelect)
            # type field uses default widget (Select) as per previous fix
            # scheme field uses default widget (Select) as it has choices in the model
            # state field uses default widget (Select) as it has choices in the model
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If a VPC is already selected (e.g. when editing an existing LB),
        # limit the choices for the subnets field to that VPC.
        # The APISelectMultiple widget with query_params handles dynamic client-side filtering.
        # This server-side filtering is for initial queryset population and validation.
        if self.instance and self.instance.pk and self.instance.vpc:
            self.fields['subnets'].queryset = AWSSubnet.objects.filter(aws_vpc=self.instance.vpc)
        elif 'vpc' in self.initial and self.initial['vpc']:
            try:
                vpc_id = int(self.initial['vpc'])
                self.fields['subnets'].queryset = AWSSubnet.objects.filter(aws_vpc_id=vpc_id)
            except (ValueError, TypeError):
                self.fields['subnets'].queryset = AWSSubnet.objects.none()
        elif self.is_bound and self.data.get('vpc'):
            try:
                vpc_id = int(self.data.get('vpc'))
                self.fields['subnets'].queryset = AWSSubnet.objects.filter(aws_vpc_id=vpc_id)
            except (ValueError, TypeError):
                 self.fields['subnets'].queryset = AWSSubnet.objects.none()
        else:
            # If no VPC is selected, no subnets can be chosen initially.
            # The dynamic JS filtering will populate this once a VPC is selected.
            self.fields['subnets'].queryset = AWSSubnet.objects.none()


class AWSLoadBalancerFilterForm(NetBoxModelFilterSetForm):
    model = AWSLoadBalancer
    filterset = AWSLoadBalancerFilterSet

    name = forms.CharField(required=False)
    arn = forms.CharField(required=False, label="ARN")
    aws_account_id = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    # region = forms.ChoiceField( # Removed region filter
    #     choices=[("", "---------")] + list(AWSLoadBalancer._meta.get_field("region").choices), required=False
    # )
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
    subnets = DynamicModelMultipleChoiceField(
        queryset=AWSSubnet.objects.all(),
        required=False,
        label="Subnets",
        widget=APISelectMultiple()
    )
    tag = TagFilterField(model)


class AWSLoadBalancerBulkEditForm(NetBoxModelBulkEditForm):
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
        label="AWS VPC",
    )
    subnets = DynamicModelMultipleChoiceField(
        queryset=AWSSubnet.objects.all(),
        required=False,
        label="Subnets",
        help_text="Select subnets to associate. Be cautious if load balancers are in different VPCs."
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
    nullable_fields = ["aws_account", "vpc", "type", "scheme", "state", "description", "comments"] # subnets can be cleared by not selecting any
