from django import forms
from ipam.models import Prefix
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField

from .models import AWSResources


class AWSResourcesForm(NetBoxModelForm):
    class Meta:
        model = AWSResources
        fields = ("name", "tags")
