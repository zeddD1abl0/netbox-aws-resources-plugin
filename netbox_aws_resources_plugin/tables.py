import django_tables2 as tables
from netbox.tables import NetBoxTable, columns

from .models import AWSVPC, AWSAccount, AWSLoadBalancer, AWSSubnet, AWSTargetGroup, AWSEC2Instance


class AWSAccountTable(NetBoxTable):
    # Define columns for the table
    account_id = tables.Column(linkify=True)  # Link to the detail view of the AWSAccount
    name = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)
    parent_account = tables.Column(linkify=True, verbose_name="Parent Account")  # Added parent_account column
    account_type = tables.Column(verbose_name="Account Type", orderable=False, empty_values=())
    # tags column is usually added by NetBoxTable if the model supports tags

    class Meta(NetBoxTable.Meta):
        model = AWSAccount
        # Fields to display in the table. Add new fields here.
        # 'pk' checkbox and 'actions' buttons are added by NetBoxTable by default.
        fields = ("pk", "id", "account_id", "name", "tenant", "parent_account", "account_type", "tags", "actions")
        default_columns = ("account_id", "name", "tenant", "parent_account", "account_type", "actions")

    def render_account_type(self, record):
        if record.parent_account is None:
            return "Root"
        return "Sub-account"


class AWSVPCTable(NetBoxTable):
    name = tables.Column(linkify=True)
    vpc_id = tables.Column(linkify=True, verbose_name="VPC ID")
    aws_account = tables.Column(linkify=True, verbose_name="AWS Account")
    region = tables.Column(verbose_name="Region")
    cidr_block = tables.Column(linkify=True, verbose_name="Primary CIDR (Prefix)")
    state = columns.ChoiceFieldColumn(verbose_name="State")
    is_default = columns.BooleanColumn(verbose_name="Is Default")
    # tags column is inherited

    class Meta(NetBoxTable.Meta):
        model = AWSVPC
        fields = (
            "pk",
            "id",
            "name",
            "vpc_id",
            "aws_account",
            "region",
            "cidr_block",
            "state",
            "is_default",
            "tags",
            "actions",
        )
        default_columns = ("name", "vpc_id", "aws_account", "region", "cidr_block", "state", "is_default", "actions")


class AWSSubnetTable(NetBoxTable):
    name = tables.Column(linkify=True)
    subnet_id = tables.Column(linkify=True, verbose_name="Subnet ID")
    aws_vpc = tables.Column(linkify=True, verbose_name="AWS VPC")
    cidr_block = tables.Column(linkify=True, verbose_name="CIDR (Prefix)")
    availability_zone = tables.Column(verbose_name="Availability Zone")
    state = columns.ChoiceFieldColumn(verbose_name="State")
    map_public_ip_on_launch = columns.BooleanColumn(verbose_name="Map Public IP")
    # tags column is inherited

    class Meta(NetBoxTable.Meta):
        model = AWSSubnet
        fields = (
            "pk",
            "id",
            "name",
            "subnet_id",
            "aws_vpc",
            "cidr_block",
            "availability_zone",
            "state",
            "map_public_ip_on_launch",
            "tags",
            "actions",
        )
        default_columns = (
            "name",
            "subnet_id",
            "aws_vpc",
            "cidr_block",
            "availability_zone",
            "state",
            "map_public_ip_on_launch",
            "actions",
        )


class AWSLoadBalancerTable(NetBoxTable):
    name = tables.Column(linkify=True)
    arn = tables.Column(linkify=True, verbose_name="ARN")
    aws_account = tables.Column(linkify=True, verbose_name="AWS Account")
    region = tables.Column(verbose_name="Region") 
    vpc = tables.Column(linkify=True, verbose_name="VPC")
    dns_name = tables.Column(verbose_name="DNS Name")


class AWSEC2InstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    instance_id = tables.Column(linkify=True, verbose_name="Instance ID")
    aws_account = tables.Column(linkify=True, verbose_name="AWS Account")
    region = tables.Column(verbose_name="Region")
    vpc = tables.Column(linkify=True, verbose_name="VPC")
    instance_type = tables.Column(verbose_name="Instance Type")
    state = columns.ChoiceFieldColumn(verbose_name="State")

    class Meta(NetBoxTable.Meta):
        model = AWSEC2Instance
        fields = (
            "pk", "id", "name", "instance_id", "aws_account", "region", "vpc", "instance_type", "state", "tags", "actions"
        )
        default_columns = ("name", "instance_id", "aws_account", "region", "vpc", "instance_type", "state", "actions") 
    subnets_count = tables.Column(verbose_name="Subnets")
    tags = columns.TagColumn(url_name='plugins:netbox_aws_resources_plugin:awsloadbalancer_list') 

    def render_subnets_count(self, record):
        return record.subnets.count()

    class Meta(NetBoxTable.Meta):
        model = AWSLoadBalancer
        fields = (
            "pk",
            "id",
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "dns_name",
            "subnets_count", 
            "type",
            "scheme",
            "state",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "dns_name",
            "subnets_count", 
            "type",
            "scheme",
            "state",
        )


class AWSTargetGroupTable(NetBoxTable):
    name = tables.Column(linkify=True)
    arn = tables.Column(linkify=True, verbose_name="ARN")
    aws_account = tables.Column(linkify=True, verbose_name="AWS Account")
    region = tables.Column(verbose_name="Region")
    vpc = tables.Column(linkify=True, verbose_name="VPC")
    protocol = tables.Column(verbose_name="Protocol")
    port = tables.Column(verbose_name="Port")
    target_type = tables.Column(verbose_name="Target Type")
    state = columns.ChoiceFieldColumn(verbose_name="State")
    load_balancers_count = tables.Column(verbose_name="LBs")
    tags = columns.TagColumn(url_name='plugins:netbox_aws_resources_plugin:awstargetgroup_list')

    def render_load_balancers_count(self, record):
        return record.load_balancers.count()

    class Meta(NetBoxTable.Meta):
        model = AWSTargetGroup
        fields = (
            "pk",
            "id",
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "protocol",
            "port",
            "target_type",
            "load_balancers_count",
            "state",
            "health_check_protocol",
            "health_check_port",
            "tags",
            "created",
            "last_updated",
            "actions",
        )
        default_columns = (
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "protocol",
            "port",
            "target_type",
            "load_balancers_count",
            "state",
        )
