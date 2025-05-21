from django.db.models import Count

from netbox.views import generic
from . import filtersets, forms, models, tables


class AWSResourcesView(generic.ObjectView):
    queryset = models.AWSResources.objects.all()


class AWSResourcesListView(generic.ObjectListView):
    queryset = models.AWSResources.objects.all()
    table = tables.AWSResourcesTable


class AWSResourcesEditView(generic.ObjectEditView):
    queryset = models.AWSResources.objects.all()
    form = forms.AWSResourcesForm


class AWSResourcesDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSResources.objects.all()
