from django import forms
from tenancy.models import Tenant
from utilities.forms.fields import DynamicModelChoiceField, TagFilterField
from netbox.forms import NetBoxModelBulkEditForm, NetBoxModelFilterSetForm, NetBoxModelForm

from ..models import AWSAccount
from ..filtersets import AWSAccountFilterSet


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
