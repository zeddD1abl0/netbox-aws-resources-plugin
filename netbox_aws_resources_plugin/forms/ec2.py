import json
from pathlib import Path
from django import forms
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from utilities.forms.widgets import APISelect
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm
from django.forms import DecimalField
from virtualization.models import VirtualMachine
from ..models import (
    AWSAccount,
    AWSVPC,
    AWSSubnet,
    AWSEC2Instance,
    AWSRDSInstance,
    EC2_INSTANCE_STATE_CHOICES,
    RDS_INSTANCE_STATE_CHOICES,
    AWS_REGION_CHOICES,
)
from ..filtersets import AWSEC2InstanceFilterSet, AWSRDSInstanceFilterSet


# Helper to load instance data from JSON
def load_instance_choices(data_type):
    json_path = Path(__file__).parent.parent / "data/instance_data.json"
    try:
        with open(json_path, "r") as f:
            data = json.load(f)

        # Get the dictionary of instances for the given data_type ('ec2' or 'rds')
        instance_dict = data.get(data_type, {})

        # Create choices from the dictionary keys (which are the instance names)
        choices = [("", "---------")]
        for instance_name in sorted(instance_dict.keys()):
            choices.append((instance_name, instance_name))

        return choices
    except (FileNotFoundError, json.JSONDecodeError):
        return [("", "---------")]


class AWSEC2InstanceForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        label="AWS Account",
    )
    region = forms.ChoiceField(
        choices=[("", "---------")] + AWS_REGION_CHOICES,
        required=True,
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        label="AWS VPC",
        required=True,
        query_params={"aws_account_id": "$aws_account", "region": "$region"},
    )
    subnet = DynamicModelChoiceField(
        queryset=AWSSubnet.objects.all(),
        label="Subnet",
        required=False,
        query_params={"aws_vpc_id": "$vpc"},
    )
    instance_type = forms.ChoiceField(
        choices=load_instance_choices("ec2"),
        required=False,
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        label="Virtual Machine",
        required=False,
    )
    estimated_cost_usd_hourly = DecimalField(
        label="Estimated Hourly Cost (USD)",
        required=False,
        disabled=True,
    )

    class Meta:
        model = AWSEC2Instance
        fields = (
            "name",
            "instance_id",
            "aws_account",
            "region",
            "vpc",
            "subnet",
            "instance_type",
            "state",
            "virtual_machine",
            "tags",
        )
        widgets = {
            "aws_account": APISelect(),
            "vpc": APISelect(),
            "subnet": APISelect(),
            "virtual_machine": APISelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["estimated_cost_usd_hourly"].initial = self.instance.estimated_cost_usd_hourly


class AWSEC2InstanceBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=AWSEC2Instance.objects.all(), widget=forms.MultipleHiddenInput)
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + AWS_REGION_CHOICES,
        required=False,
    )
    vpc = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="VPC")
    state = forms.ChoiceField(
        choices=[("", "---------")] + EC2_INSTANCE_STATE_CHOICES,
        required=False,
    )

    class Meta:
        nullable_fields = ["vpc"]


class AWSEC2InstanceFilterForm(NetBoxModelFilterSetForm):
    model = AWSEC2Instance
    filterset = AWSEC2InstanceFilterSet

    aws_account_id = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + AWS_REGION_CHOICES,
        required=False,
    )
    vpc_id = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="VPC")
    state = forms.ChoiceField(
        choices=[("", "---------")] + EC2_INSTANCE_STATE_CHOICES,
        required=False,
    )
    virtual_machine_id = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label="Virtual Machine"
    )
    tag = TagFilterField(model)


class AWSRDSInstanceForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        label="AWS Account",
    )
    region = forms.ChoiceField(
        choices=[("", "---------")] + AWS_REGION_CHOICES,
        required=True,
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        label="AWS VPC",
        required=True,
        query_params={"aws_account_id": "$aws_account", "region": "$region"},
    )
    subnet = DynamicModelChoiceField(
        queryset=AWSSubnet.objects.all(),
        label="Subnet",
        required=False,
        query_params={"aws_vpc_id": "$vpc"},
    )
    instance_class = forms.ChoiceField(choices=load_instance_choices("rds"), required=False, label="Instance Class")
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        label="Virtual Machine",
        required=False,
    )
    estimated_cost_usd_hourly = DecimalField(
        label="Estimated Hourly Cost (USD)",
        required=False,
        disabled=True,
    )

    class Meta:
        model = AWSRDSInstance
        fields = (
            "name",
            "instance_id",
            "aws_account",
            "region",
            "vpc",
            "subnet",
            "instance_class",
            "engine",
            "engine_version",
            "state",
            "virtual_machine",
            "tags",
        )
        widgets = {
            "aws_account": APISelect(),
            "vpc": APISelect(),
            "subnet": APISelect(),
            "virtual_machine": APISelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["estimated_cost_usd_hourly"].initial = self.instance.estimated_cost_usd_hourly


class AWSRDSInstanceBulkEditForm(NetBoxModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=AWSRDSInstance.objects.all(), widget=forms.MultipleHiddenInput)
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + AWS_REGION_CHOICES,
        required=False,
    )
    vpc = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="VPC")
    state = forms.ChoiceField(
        choices=[("", "---------")] + RDS_INSTANCE_STATE_CHOICES,
        required=False,
    )

    class Meta:
        nullable_fields = ["vpc"]


class AWSRDSInstanceFilterForm(NetBoxModelFilterSetForm):
    model = AWSRDSInstance
    filterset = AWSRDSInstanceFilterSet

    aws_account_id = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    region = forms.ChoiceField(
        choices=[("", "---------")] + AWS_REGION_CHOICES,
        required=False,
    )
    vpc_id = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="VPC")
    state = forms.ChoiceField(
        choices=[("", "---------")] + RDS_INSTANCE_STATE_CHOICES,
        required=False,
    )
    virtual_machine_id = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(), required=False, label="Virtual Machine"
    )
    tag = TagFilterField(model)
