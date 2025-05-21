from netbox.views import generic

from . import filtersets, forms, models, tables


class AWSAccountView(generic.ObjectView):
    queryset = models.AWSAccount.objects.all()


class AWSAccountListView(generic.ObjectListView):
    queryset = models.AWSAccount.objects.all()
    table = tables.AWSAccountTable
    filterset = filtersets.AWSAccountFilterSet
    filterset_form = forms.AWSAccountFilterForm


class AWSAccountEditView(generic.ObjectEditView):
    queryset = models.AWSAccount.objects.all()
    form = forms.AWSAccountForm


class AWSAccountDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSAccount.objects.all()


# Views for Bulk Operations
class AWSAccountBulkEditView(generic.BulkEditView):
    queryset = models.AWSAccount.objects.all()
    filterset = filtersets.AWSAccountFilterSet  # Optional: To pre-filter items if navigating from a filtered list
    table = tables.AWSAccountTable
    form = forms.AWSAccountBulkEditForm


class AWSAccountBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSAccount.objects.all()
    table = tables.AWSAccountTable


# Views for AWSVPC


class AWSVPCView(generic.ObjectView):
    queryset = models.AWSVPC.objects.select_related("aws_account", "cidr_block")
    # Template: netbox_aws_resources_plugin/awsvpc.html (lowercase model name)

    def get_extra_context(self, request, instance):
        # Get related subnets
        subnets = models.AWSSubnet.objects.filter(aws_vpc=instance).select_related(
            "cidr_block", "aws_vpc__aws_account"  # Optimize query for table display
        )
        awssubnet_table = tables.AWSSubnetTable(subnets)
        awssubnet_table.configure(request)

        return {
            "awssubnet_table": awssubnet_table,
        }


class AWSVPCListView(generic.ObjectListView):
    queryset = models.AWSVPC.objects.select_related("aws_account", "cidr_block")
    table = tables.AWSVPCTable
    filterset = filtersets.AWSVPCFilterSet
    filterset_form = forms.AWSVPCFilterForm


class AWSVPCEditView(generic.ObjectEditView):
    queryset = models.AWSVPC.objects.all()
    form = forms.AWSVPCForm
    # template_name = 'netbox_aws_resources_plugin/awsvpc_edit.html' # Optional


class AWSVPCDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSVPC.objects.all()
    # template_name = 'netbox_aws_resources_plugin/awsvpc_delete.html' # Optional


class AWSVPCBulkEditView(generic.BulkEditView):
    queryset = models.AWSVPC.objects.select_related("aws_account", "region", "cidr_block")
    filterset = filtersets.AWSVPCFilterSet
    table = tables.AWSVPCTable
    form = forms.AWSVPCBulkEditForm


class AWSVPCBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSVPC.objects.all()
    table = tables.AWSVPCTable


# Views for AWSSubnet


class AWSSubnetView(generic.ObjectView):
    queryset = models.AWSSubnet.objects.select_related("aws_vpc", "cidr_block", "aws_vpc__aws_account")
    # Template: netbox_aws_resources_plugin/awssubnet.html


class AWSSubnetListView(generic.ObjectListView):
    queryset = models.AWSSubnet.objects.select_related("aws_vpc", "cidr_block", "aws_vpc__aws_account")
    table = tables.AWSSubnetTable
    filterset = filtersets.AWSSubnetFilterSet
    filterset_form = forms.AWSSubnetFilterForm


class AWSSubnetEditView(generic.ObjectEditView):
    queryset = models.AWSSubnet.objects.all()
    form = forms.AWSSubnetForm
    # template_name = 'netbox_aws_resources_plugin/awssubnet_edit.html' # Optional


class AWSSubnetDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSSubnet.objects.all()
    # template_name = 'netbox_aws_resources_plugin/awssubnet_delete.html' # Optional


class AWSSubnetBulkEditView(generic.BulkEditView):
    queryset = models.AWSSubnet.objects.select_related("aws_vpc", "cidr_block", "aws_vpc__aws_account")
    filterset = filtersets.AWSSubnetFilterSet
    table = tables.AWSSubnetTable
    form = forms.AWSSubnetBulkEditForm


class AWSSubnetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSSubnet.objects.all()
    table = tables.AWSSubnetTable


# Views for AWSLoadBalancer


class AWSLoadBalancerView(generic.ObjectView):
    queryset = models.AWSLoadBalancer.objects.all()
    # NetBox will conventionally look for a template at
    # netbox_aws_resources_plugin/awsloadbalancer.html (lowercase model name)
    # We will create this template later if specific customizations are needed beyond generic/object.html


class AWSLoadBalancerListView(generic.ObjectListView):
    queryset = models.AWSLoadBalancer.objects.all()
    table = tables.AWSLoadBalancerTable
    filterset = filtersets.AWSLoadBalancerFilterSet
    filterset_form = forms.AWSLoadBalancerFilterForm


class AWSLoadBalancerEditView(generic.ObjectEditView):
    queryset = models.AWSLoadBalancer.objects.all()
    form = forms.AWSLoadBalancerForm
    # template_name = 'netbox_aws_resources_plugin/awsloadbalancer_edit.html' # Optional


class AWSLoadBalancerDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSLoadBalancer.objects.all()
    # template_name = 'netbox_aws_resources_plugin/awsloadbalancer_delete.html' # Optional


class AWSLoadBalancerBulkEditView(generic.BulkEditView):
    queryset = models.AWSLoadBalancer.objects.select_related("aws_account", "vpc", "region")  # Optimize query
    filterset = filtersets.AWSLoadBalancerFilterSet
    table = tables.AWSLoadBalancerTable
    form = forms.AWSLoadBalancerBulkEditForm


class AWSLoadBalancerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSLoadBalancer.objects.all()
    table = tables.AWSLoadBalancerTable
