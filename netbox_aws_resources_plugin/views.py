from netbox.views import generic
from ipam.tables import IPAddressTable  # noqa # type: ignore
from ipam.models import IPAddress  # noqa # type: ignore

from . import filtersets, forms, models, tables


class AWSAccountView(generic.ObjectView):
    queryset = models.AWSAccount.objects.prefetch_related("tags", "child_accounts")

    def get_extra_context(self, request, instance):
        # Child Accounts Table
        child_accounts = instance.child_accounts.all()
        child_accounts_table = tables.AWSAccountTable(child_accounts, user=request.user, exclude=("parent_account",))
        child_accounts_table.configure(request)

        # Related VPCs Table
        vpcs = instance.vpcs.all().select_related("aws_account", "region", "cidr_block")
        aws_vpc_table = tables.AWSVPCTable(vpcs, user=request.user, exclude=("aws_account",))
        aws_vpc_table.configure(request)

        # Related Load Balancers Table (assuming related_name='load_balancers' on AWSLoadBalancer model for AWSAccount)
        # If the related_name is different, this line will need adjustment.
        # For example, if AWSLoadBalancer.aws_account has related_name="account_load_balancers"
        load_balancers = models.AWSLoadBalancer.objects.filter(aws_account=instance).select_related(
            "aws_account", "region", "vpc"
        )
        aws_load_balancer_table = tables.AWSLoadBalancerTable(
            load_balancers, user=request.user, exclude=("aws_account",)
        )
        aws_load_balancer_table.configure(request)

        return {
            "child_accounts_table": child_accounts_table,
            "aws_vpc_table": aws_vpc_table,
            "aws_load_balancer_table": aws_load_balancer_table,
        }


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
        # Table of associated Load Balancers
        # Use the related_name 'vpc_load_balancers' from AWSLoadBalancer.vpc field
        load_balancers = instance.vpc_load_balancers.all().select_related(
            "aws_account", "vpc"
        )  # Removed 'region' from select_related
        load_balancers_table = tables.AWSLoadBalancerTable(load_balancers, user=request.user)
        load_balancers_table.configure(request)

        # Table of associated Subnets
        subnets = models.AWSSubnet.objects.filter(aws_vpc=instance).select_related(
            "cidr_block", "aws_vpc__aws_account"  # Optimize query for table display
        )
        awssubnet_table = tables.AWSSubnetTable(subnets, user=request.user)
        awssubnet_table.configure(request)

        return {
            "awssubnet_table": awssubnet_table,
            "awsloadbalancer_table": load_balancers_table,
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


#
# Views for AWSEC2Instance
#


class AWSEC2InstanceView(generic.ObjectView):
    queryset = models.AWSEC2Instance.objects.select_related("aws_account", "vpc", "virtual_machine")

    def get_extra_context(self, request, instance):
        return {
            "virtual_machine": instance.virtual_machine,
        }


class AWSEC2InstanceListView(generic.ObjectListView):
    queryset = models.AWSEC2Instance.objects.select_related("aws_account", "vpc")
    table = tables.AWSEC2InstanceTable
    filterset = filtersets.AWSEC2InstanceFilterSet
    filterset_form = forms.AWSEC2InstanceFilterForm


class AWSEC2InstanceEditView(generic.ObjectEditView):
    queryset = models.AWSEC2Instance.objects.all()
    form = forms.AWSEC2InstanceForm


class AWSEC2InstanceDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSEC2Instance.objects.all()


class AWSEC2InstanceBulkEditView(generic.BulkEditView):
    queryset = models.AWSEC2Instance.objects.select_related("aws_account", "vpc")
    filterset = filtersets.AWSEC2InstanceFilterSet
    table = tables.AWSEC2InstanceTable
    form = forms.AWSEC2InstanceBulkEditForm


class AWSEC2InstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSEC2Instance.objects.all()
    table = tables.AWSEC2InstanceTable


#
# Views for AWSRDSInstance
#


class AWSRDSInstanceView(generic.ObjectView):
    queryset = models.AWSRDSInstance.objects.select_related("aws_account", "vpc", "virtual_machine")

    def get_extra_context(self, request, instance):
        return {
            "virtual_machine": instance.virtual_machine,
        }


class AWSRDSInstanceListView(generic.ObjectListView):
    queryset = models.AWSRDSInstance.objects.select_related("aws_account", "vpc")
    table = tables.AWSRDSInstanceTable
    filterset = filtersets.AWSRDSInstanceFilterSet
    filterset_form = forms.AWSRDSInstanceFilterForm


class AWSRDSInstanceEditView(generic.ObjectEditView):
    queryset = models.AWSRDSInstance.objects.all()
    form = forms.AWSRDSInstanceForm


class AWSRDSInstanceDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSRDSInstance.objects.all()


class AWSRDSInstanceBulkEditView(generic.BulkEditView):
    queryset = models.AWSRDSInstance.objects.select_related("aws_account", "vpc")
    filterset = filtersets.AWSRDSInstanceFilterSet
    table = tables.AWSRDSInstanceTable
    form = forms.AWSRDSInstanceBulkEditForm


class AWSRDSInstanceBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSRDSInstance.objects.all()
    table = tables.AWSRDSInstanceTable


# Views for AWSSubnet


class AWSSubnetView(generic.ObjectView):
    queryset = models.AWSSubnet.objects.select_related("aws_vpc__aws_account", "cidr_block")

    def get_extra_context(self, request, instance):
        # Get IP Addresses in this subnet
        ip_addresses = IPAddress.objects.none()  # Default to no IPs
        if instance.cidr_block:  # Ensure the subnet has a CIDR block assigned
            ip_addresses = (
                IPAddress.objects.restrict(request.user, "view")
                .filter(
                    address__net_contained=str(instance.cidr_block)  # Filter IPs contained within the subnet's prefix
                )
                .select_related("vrf", "tenant")
            )

        ip_addresses_table = IPAddressTable(ip_addresses, user=request.user)
        if not request.user.has_perm("ipam.view_ipaddress"):
            ip_addresses_table = None  # Clear table if no permission
        elif ip_addresses_table:
            ip_addresses_table.configure(request)

        return {
            "ip_addresses_table": ip_addresses_table,
        }


class AWSSubnetListView(generic.ObjectListView):
    queryset = models.AWSSubnet.objects.select_related("aws_vpc", "cidr_block", "aws_vpc__aws_account")
    table = tables.AWSSubnetTable
    filterset = filtersets.AWSSubnetFilterSet
    filterset_form = forms.AWSSubnetFilterForm


class AWSSubnetEditView(generic.ObjectEditView):
    queryset = models.AWSSubnet.objects.all()
    form = forms.AWSSubnetForm
    template_name = "netbox_aws_resources_plugin/awssubnet_edit.html"


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
    queryset = models.AWSLoadBalancer.objects.select_related("aws_account", "vpc").prefetch_related("subnets", "tags")

    def get_extra_context(self, request, instance):
        # Get the context from the parent view
        context = super().get_extra_context(request, instance)

        # Prepare and add the subnets table
        aws_subnets_table = tables.AWSSubnetTable(instance.subnets.all(), user=request.user)
        aws_subnets_table.configure(request)
        context["aws_subnets_table"] = aws_subnets_table

        return context


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


# Views for AWSTargetGroup


class AWSTargetGroupView(generic.ObjectView):
    queryset = models.AWSTargetGroup.objects.select_related("aws_account", "vpc").prefetch_related(
        "load_balancers", "tags"
    )

    def get_extra_context(self, request, instance):
        # Associated Load Balancers Table
        load_balancers_table = tables.AWSLoadBalancerTable(instance.load_balancers.all(), user=request.user)
        load_balancers_table.configure(request)

        return {
            "load_balancers_table": load_balancers_table,
        }


class AWSTargetGroupListView(generic.ObjectListView):
    queryset = models.AWSTargetGroup.objects.select_related("aws_account", "vpc").prefetch_related(
        "load_balancers", "tags"
    )
    table = tables.AWSTargetGroupTable
    filterset = filtersets.AWSTargetGroupFilterSet
    filterset_form = forms.AWSTargetGroupFilterForm


class AWSTargetGroupEditView(generic.ObjectEditView):
    queryset = models.AWSTargetGroup.objects.all()
    form = forms.AWSTargetGroupForm


class AWSTargetGroupDeleteView(generic.ObjectDeleteView):
    queryset = models.AWSTargetGroup.objects.all()


class AWSTargetGroupBulkEditView(generic.BulkEditView):
    queryset = models.AWSTargetGroup.objects.select_related("aws_account", "vpc").prefetch_related(
        "load_balancers", "tags"
    )
    filterset = filtersets.AWSTargetGroupFilterSet
    table = tables.AWSTargetGroupTable
    form = forms.AWSTargetGroupBulkEditForm


class AWSTargetGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = models.AWSTargetGroup.objects.all()
    table = tables.AWSTargetGroupTable
