from netbox.filtersets import NetBoxModelFilterSet
from .models import AWSResources


# class AWSResourcesFilterSet(NetBoxModelFilterSet):
#
#     class Meta:
#         model = AWSResources
#         fields = ['name', ]
#
#     def search(self, queryset, name, value):
#         return queryset.filter(description__icontains=value)
