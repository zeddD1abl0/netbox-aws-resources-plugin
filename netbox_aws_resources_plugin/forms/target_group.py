from django import forms
from utilities.forms import add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.widgets import APISelect, APISelectMultiple
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelBulkEditForm

from ipam.models import Service
from ..models import (
    AWSAccount,
    AWSVPC,
    AWSLoadBalancer,
    AWSTargetGroup,
    TARGET_GROUP_TYPE_CHOICES,
    AWS_TARGET_GROUP_STATE_CHOICES,
    TARGET_GROUP_HEALTH_CHECK_PROTOCOL_CHOICES,
)
from ..filtersets import AWSTargetGroupFilterSet


class AWSTargetGroupForm(NetBoxModelForm):
    aws_account = DynamicModelChoiceField(
        queryset=AWSAccount.objects.all(),
        label="AWS Account",
        help_text="The AWS account this Target Group belongs to",
    )
    vpc = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        label="AWS VPC",
        help_text="The AWS VPC this Target Group is associated with. Region is derived from this VPC.",
        query_params={"aws_account_id": "$aws_account"},
    )
    service = DynamicModelChoiceField(
        queryset=Service.objects.all(),
        required=False,
        label="Service",
        help_text="Service (port and protocol) associated with this Target Group",
    )
    load_balancers = DynamicModelMultipleChoiceField(
        queryset=AWSLoadBalancer.objects.all(),
        required=False,
        label="Associated Load Balancers",
        help_text="Load Balancers to associate with this Target Group. Must be in the same AWS Account and VPC.",
        query_params={"aws_account_id": "$aws_account", "vpc_id": "$vpc"},
    )

    class Meta:
        model = AWSTargetGroup
        fields = (
            "name",
            "arn",
            "aws_account",
            "vpc",
            "service",
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
        )
        widgets = {
            "aws_account": APISelect(attrs={"data-dynamic-parameters": "region_id"}),
            "vpc": APISelect(),
            "load_balancers": APISelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")

        # If an AWS Account is selected, filter VPCs and Load Balancers by it
        if self.is_bound:
            account_id = self.data.get("aws_account")
            vpc_id = self.data.get("vpc")
        elif instance and instance.pk:
            account_id = instance.aws_account_id
            vpc_id = instance.vpc_id
        else:
            account_id = self.initial.get("aws_account")
            vpc_id = self.initial.get("vpc")

        if account_id:
            self.fields["vpc"].queryset = AWSVPC.objects.filter(aws_account_id=account_id)
            if vpc_id:  # If VPC for the Target Group is known
                self.fields["load_balancers"].queryset = AWSLoadBalancer.objects.filter(
                    aws_account_id=account_id, vpc_id=vpc_id  # LBs must be in the same account and SAME VPC as the TG
                )
            else:  # VPC for the Target Group is not yet selected/known (e.g. initial form load for new TG)
                self.fields["load_balancers"].queryset = AWSLoadBalancer.objects.none()
        else:  # Account for the Target Group is not yet selected/known
            self.fields["vpc"].queryset = AWSVPC.objects.none()
            self.fields["load_balancers"].queryset = AWSLoadBalancer.objects.none()


class AWSTargetGroupFilterForm(NetBoxModelFilterSetForm):
    model = AWSTargetGroup
    filterset = AWSTargetGroupFilterSet

    name = forms.CharField(required=False)
    arn = forms.CharField(required=False, label="ARN")
    aws_account_id = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    vpc_id = DynamicModelChoiceField(
        queryset=AWSVPC.objects.all(),
        required=False,
        label="AWS VPC",
        query_params={"aws_account_id": "$aws_account_id"},
    )
    service_id = DynamicModelChoiceField(queryset=Service.objects.all(), required=False, label="Service")
    target_type = forms.ChoiceField(choices=add_blank_choice(TARGET_GROUP_TYPE_CHOICES), required=False)
    state = forms.ChoiceField(choices=add_blank_choice(AWS_TARGET_GROUP_STATE_CHOICES), required=False)
    load_balancer_id = DynamicModelMultipleChoiceField(
        queryset=AWSLoadBalancer.objects.all(), required=False, label="Load Balancers", widget=APISelectMultiple()
    )
    tag = TagFilterField(model)


class AWSTargetGroupBulkEditForm(NetBoxModelBulkEditForm):
    aws_account = DynamicModelChoiceField(queryset=AWSAccount.objects.all(), required=False, label="AWS Account")
    vpc = DynamicModelChoiceField(queryset=AWSVPC.objects.all(), required=False, label="AWS VPC")
    service = DynamicModelChoiceField(queryset=Service.objects.all(), required=False, label="Service")
    target_type = forms.ChoiceField(
        choices=add_blank_choice(TARGET_GROUP_TYPE_CHOICES), required=False, widget=forms.Select
    )
    state = forms.ChoiceField(
        choices=add_blank_choice(AWS_TARGET_GROUP_STATE_CHOICES), required=False, widget=forms.Select
    )

    health_check_protocol = forms.ChoiceField(
        choices=add_blank_choice(TARGET_GROUP_HEALTH_CHECK_PROTOCOL_CHOICES), required=False, widget=forms.Select
    )
    health_check_port = forms.CharField(required=False, help_text="Port for health checks (default: 'traffic-port')")
    health_check_path = forms.CharField(required=False, help_text="Destination for HTTP/HTTPS health checks")
    health_check_interval_seconds = forms.IntegerField(
        required=False, help_text="Approximate interval between health checks (seconds)"
    )
    health_check_timeout_seconds = forms.IntegerField(
        required=False, help_text="Timeout for a health check response (seconds)"
    )
    healthy_threshold_count = forms.IntegerField(
        required=False, help_text="Number of consecutive successful health checks to become healthy"
    )
    unhealthy_threshold_count = forms.IntegerField(
        required=False, help_text="Number of consecutive failed health checks to become unhealthy"
    )

    model = AWSTargetGroup
    nullable_fields = [
        "arn",
        "aws_account",
        "vpc",
        "service",
        "target_type",
        "state",
        "health_check_protocol",
        "health_check_port",
        "health_check_path",
        "health_check_interval_seconds",
        "health_check_timeout_seconds",
        "healthy_threshold_count",
        "unhealthy_threshold_count",
    ]
