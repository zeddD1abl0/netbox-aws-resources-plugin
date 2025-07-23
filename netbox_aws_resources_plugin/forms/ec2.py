from django import forms
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from utilities.forms.widgets import APISelect
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from ..models import AWSAccount, AWSVPC, AWSEC2Instance, EC2_INSTANCE_STATE_CHOICES, AWS_REGION_CHOICES
from ..filtersets import AWSEC2InstanceFilterSet


class AWSEC2InstanceForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        label="AWS Account",
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        label="AWS VPC",
        required=False,
        query_params={"aws_account_id": "$aws_account"},
    )

    class Meta:
        model = AWSEC2Instance
        fields = (
            'name', 'instance_id', 'aws_account', 'region', 'vpc', 'instance_type', 'state', 'tags'
        )
        widgets = {
            "aws_account": APISelect(),
            "vpc": APISelect(),
        }


class AWSEC2InstanceBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=AWSEC2Instance.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
        label='AWS Account'
    )
    region = forms.ChoiceField(
        choices=[('', '---------')] + AWS_REGION_CHOICES,
        required=False,
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
        label='VPC'
    )
    state = forms.ChoiceField(
        choices=[('', '---------')] + EC2_INSTANCE_STATE_CHOICES,
        required=False,
    )

    class Meta:
        nullable_fields = ['vpc']


class AWSEC2InstanceFilterForm(NetBoxModelFilterSetForm):
    model = AWSEC2Instance
    filterset = AWSEC2InstanceFilterSet

    aws_account_id = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        required=False,
        label='AWS Account'
    )
    region = forms.ChoiceField(
        choices=[('', '---------')] + AWS_REGION_CHOICES,
        required=False,
    )
    vpc_id = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
        label='VPC'
    )
    state = forms.ChoiceField(
        choices=[('', '---------')] + EC2_INSTANCE_STATE_CHOICES,
        required=False,
    )
    tag = TagFilterField(model)
