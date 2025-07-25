import django_tables2 as tables
from . import models
from netbox.tables import NetBoxTable, columns

from .models import AWSVPC, AWSAccount, AWSSubnet, AWSTargetGroup, AWSEC2Instance, AWSRDSInstance


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
    aws_account = tables.TemplateColumn(
        template_code="""
        {% if record.aws_account %}
            <a href="{% url 'plugins:netbox_aws_resources_plugin:awsaccount' pk=record.aws_account.pk %}">
                {{ record.aws_account }}
            </a>
        {% else %}
            &mdash;
        {% endif %}
        """
    )
    region = tables.TemplateColumn(template_code="{{ record.region|default:'&mdash;' }}")
    vpc = tables.TemplateColumn(
        template_code="""
        {% if record.vpc %}
            <a href="{% url 'plugins:netbox_aws_resources_plugin:awsvpc' pk=record.vpc.pk %}">{{ record.vpc }}</a>
        {% else %}
            &mdash;
        {% endif %}
        """
    )
    dns_name = tables.Column(verbose_name="DNS Name")

    class Meta(NetBoxTable.Meta):
        model = models.AWSLoadBalancer
        fields = (
            "pk",
            "id",
            "name",
            "arn",
            "aws_account",
            "region",
            "vpc",
            "dns_name",
            "state",
            "type",
            "scheme",
            "ip_address_type",
            "actions",
        )
        default_columns = ("name", "arn", "aws_account", "region", "vpc", "dns_name", "state", "type")


class AWSEC2InstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    instance_id = tables.Column(linkify=True, verbose_name="Instance ID")
    aws_account = tables.Column(linkify=True, verbose_name="AWS Account")
    region = tables.Column(verbose_name="Region")
    vpc = tables.Column(linkify=True, verbose_name="VPC")
    instance_type = tables.Column(verbose_name="Instance Type")
    state = columns.ChoiceFieldColumn(verbose_name="State")
    estimated_cost_usd_hourly = tables.Column(verbose_name="Est. Hourly Cost (USD)")

    class Meta(NetBoxTable.Meta):
        model = AWSEC2Instance
        fields = (
            "pk",
            "id",
            "name",
            "instance_id",
            "aws_account",
            "region",
            "vpc",
            "instance_type",
            "state",
            "estimated_cost_usd_hourly",
            "tags",
            "actions",
        )
        default_columns = (
            "name",
            "instance_id",
            "aws_account",
            "region",
            "vpc",
            "instance_type",
            "state",
            "estimated_cost_usd_hourly",
            "actions",
        )


class AWSRDSInstanceTable(NetBoxTable):
    name = tables.Column(linkify=True)
    instance_id = tables.Column(linkify=True, verbose_name="DB Identifier")
    aws_account = tables.Column(linkify=True, verbose_name="AWS Account")
    region = tables.Column(verbose_name="Region")
    vpc = tables.Column(linkify=True, verbose_name="VPC")
    instance_class = tables.Column(verbose_name="Instance Class")
    engine = tables.Column(verbose_name="Engine")
    engine_version = tables.Column(verbose_name="Engine Version")
    state = columns.ChoiceFieldColumn(verbose_name="State")
    estimated_cost_usd_hourly = tables.Column(verbose_name="Est. Hourly Cost (USD)")

    class Meta(NetBoxTable.Meta):
        model = AWSRDSInstance
        fields = (
            "pk",
            "id",
            "name",
            "instance_id",
            "aws_account",
            "region",
            "vpc",
            "instance_class",
            "engine",
            "engine_version",
            "state",
            "estimated_cost_usd_hourly",
            "tags",
            "actions",
        )
        default_columns = (
            "name",
            "instance_id",
            "aws_account",
            "region",
            "vpc",
            "instance_class",
            "engine",
            "state",
            "estimated_cost_usd_hourly",
            "actions",
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
    tags = columns.TagColumn(url_name="plugins:netbox_aws_resources_plugin:awstargetgroup_list")

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
