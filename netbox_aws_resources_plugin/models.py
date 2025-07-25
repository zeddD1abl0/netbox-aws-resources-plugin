import json
from pathlib import Path
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from ipam.models import Prefix, Service  # Import NetBox Prefix model
from netbox.models import NetBoxModel
from tenancy.models import Tenant
from virtualization.models import VirtualMachine


class AWSAccount(NetBoxModel):
    account_id = models.CharField(
        max_length=12, unique=True, help_text="AWS Account ID (12 digits)", blank=True, null=True
    )
    name = models.CharField(max_length=100, help_text="Descriptive name for the AWS account")
    tenant = models.ForeignKey(to=Tenant, on_delete=models.PROTECT, related_name="aws_accounts", blank=True, null=True)
    # New field for parent-child relationship
    parent_account = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,  # If a parent is deleted, children become root accounts
        related_name="child_accounts",
        null=True,
        blank=True,
        verbose_name="Parent AWS Account",
        help_text="The root account if this is a member (sub) account.",
    )

    # Properties for search indexing
    @property
    def search_parent_name(self):
        if self.parent_account:
            return self.parent_account.name
        return None

    @property
    def search_parent_account_id(self):
        if self.parent_account:
            return self.parent_account.account_id
        return None

    class Meta:
        ordering = ("account_id", "name")
        verbose_name = "AWS Account"
        verbose_name_plural = "AWS Accounts"

    def __str__(self):
        if self.name:
            return f"{self.account_id} ({self.name})"
        return self.account_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_resources_plugin:awsaccount", args=[self.pk])


# Helper function to load region choices from JSON
def load_region_choices():
    """
    Loads AWS region choices from a JSON file and formats them for display.
    Example format: ap-southeast-2 (Asia Pacific - Sydney)
    """
    try:
        data_file = Path(__file__).parent / "data" / "region_data.json"
        with open(data_file, "r") as f:
            region_data = json.load(f)

        formatted_choices = []
        for code, name in region_data.items():
            # Reformat name from "Location (City)" to "Location - City"
            formatted_name = name.replace(" (", " - ").replace(")", "")
            display_name = f"{code} ({formatted_name})"
            formatted_choices.append((code, display_name))

        # Sort by the full display name
        return sorted(formatted_choices, key=lambda item: item[1])

    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to an empty list if the file is missing or invalid
        return []


# Choices for model fields
AWS_REGION_CHOICES = load_region_choices()

LOADBALANCER_TYPE_CHOICES = [
    ("application", "Application"),
    ("network", "Network"),
    ("gateway", "Gateway"),
]

LOADBALANCER_SCHEME_CHOICES = [
    ("internal", "Internal"),
    ("internet-facing", "Internet-facing"),
]

LOADBALANCER_STATE_CHOICES = [
    ("planned", "Planned"),
    ("active", "Active"),
    ("provisioning", "Provisioning"),
    ("active_impaired", "Active Impaired"),
    ("failed", "Failed"),
    ("unknown", "Unknown"),
]

AWS_VPC_STATE_CHOICES = [
    ("planned", "Planned"),
    ("pending", "Pending"),
    ("available", "Available"),
]

AWS_SUBNET_STATE_CHOICES = [
    ("planned", "Planned"),
    ("pending", "Pending"),
    ("available", "Available"),
]

# Choices for TargetGroup model fields
TARGET_GROUP_PROTOCOL_CHOICES = [
    ("HTTP", "HTTP"),
    ("HTTPS", "HTTPS"),
    ("TCP", "TCP"),
    ("TLS", "TLS"),
    ("UDP", "UDP"),
    ("TCP_UDP", "TCP_UDP"),
    ("GENEVE", "GENEVE"),
]

TARGET_GROUP_TYPE_CHOICES = [
    ("instance", "EC2 Instance"),
    ("ip", "IP Address"),
    # ('lambda', 'Lambda function'), # Lambda targets are not supported by this plugin model
    ("alb", "Application Load Balancer"),
]

TARGET_GROUP_HEALTH_CHECK_PROTOCOL_CHOICES = [
    ("HTTP", "HTTP"),
    ("HTTPS", "HTTPS"),
    ("TCP", "TCP"),
]

AWS_TARGET_GROUP_STATE_CHOICES = [
    ("planned", "Planned"),
    ("creating", "Creating"),
    ("active", "Active"),
    ("deleting", "Deleting"),
    ("failed", "Failed"),
]


class AWSVPC(NetBoxModel):
    aws_account = models.ForeignKey(
        to=AWSAccount, on_delete=models.PROTECT, related_name="vpcs", help_text="The AWS Account this VPC belongs to"
    )
    name = models.CharField(max_length=255, help_text="The name of the VPC")
    vpc_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="VPC ID",
        help_text="The unique identifier for the VPC (e.g., vpc-012345abcdef)",
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the VPC is located"
    )
    # Represents the primary IPv4 CIDR block. Additional CIDR blocks are handled via ipam.Prefix relationships if needed
    cidr_block = (
        models.OneToOneField(  # A VPC has one primary CIDR block in AWS, often represented as a Prefix in NetBox
            to="ipam.Prefix",
            on_delete=models.PROTECT,  # Protecting the Prefix if a VPC references it
            related_name="aws_vpc_primary_cidr",  # Ensure this related_name is unique if used elsewhere
            help_text="The primary IPv4 CIDR block for this VPC.",
        )
    )
    state = models.CharField(
        max_length=30, choices=AWS_VPC_STATE_CHOICES, default="available", help_text="The current state of the VPC"
    )
    is_default = models.BooleanField(default=False, help_text="Whether this is the default VPC for the account/region")

    class Meta:
        ordering = ("name", "vpc_id", "region", "aws_account")
        verbose_name = "AWS VPC"
        verbose_name_plural = "AWS VPCs"
        constraints = [
            models.UniqueConstraint(
                fields=["aws_account", "region", "vpc_id"],  # VPC ID is unique per region, but account adds safety
                name="unique_awsvpc_account_region_vpcid",
            )
        ]

    def clean(self):
        super().clean()
        # The assigned Prefix for a VPC cannot be a child prefix.
        if self.cidr_block and self.cidr_block.prefix:
            raise ValidationError({"cidr_block": "The selected Prefix cannot be a child of another Prefix."})

    def __str__(self):
        return self.name or self.vpc_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_resources_plugin:awsvpc", args=[self.pk])


class AWSSubnet(NetBoxModel):
    aws_vpc = models.ForeignKey(
        to=AWSVPC, on_delete=models.PROTECT, related_name="subnets", help_text="The AWS VPC this Subnet belongs to"
    )
    name = models.CharField(max_length=255, help_text="The name of the Subnet")
    subnet_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Subnet ID",
        help_text="The unique identifier for the Subnet (e.g., subnet-012345abcdef)",
    )
    # Represents the IPv4 CIDR block of the subnet.
    cidr_block = models.OneToOneField(  # A Subnet has one CIDR block, represented as a Prefix in NetBox
        to=Prefix,
        on_delete=models.PROTECT,  # Protecting the Prefix if a Subnet references it
        related_name="aws_subnet_cidr",
        null=True,  # Can be null if not yet provisioned or if managed differently
        blank=True,
        help_text="The IPv4 CIDR block of this Subnet, represented as a NetBox Prefix",
    )
    availability_zone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Availability Zone",
        help_text="The Availability Zone of the Subnet (e.g., us-east-1a)",
    )
    availability_zone_id = models.CharField(
        max_length=50, blank=True, verbose_name="AZ ID", help_text="The ID of the Availability Zone (e.g., use1-az1)"
    )
    state = models.CharField(
        max_length=30,
        choices=AWS_SUBNET_STATE_CHOICES,
        default="available",
        help_text="The current state of the Subnet",
    )
    map_public_ip_on_launch = models.BooleanField(
        default=False,
        verbose_name="Map Public IP on launch",
        help_text="Whether instances in this subnet get a public IP on launch by default",
    )

    def clean(self):
        super().clean()
        if self.cidr_block and self.aws_vpc:
            # The assigned Prefix for a Subnet must be a child of the VPC's Prefix.
            if not self.cidr_block.prefix or self.cidr_block.prefix != self.aws_vpc.cidr_block:
                raise ValidationError(
                    {"cidr_block": f"The Prefix must be a child of the parent VPC Prefix ({self.aws_vpc.cidr_block})."}
                )

    class Meta:
        ordering = ("aws_vpc", "cidr_block")
        verbose_name = "AWS Subnet"
        verbose_name_plural = "AWS Subnets"
        constraints = [
            models.UniqueConstraint(
                fields=["aws_vpc", "subnet_id"],  # Subnet ID is unique within a VPC
                name="unique_awssubnet_vpc_subnetid",
            )
        ]

    def __str__(self):
        return self.name or self.subnet_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_resources_plugin:awssubnet", args=[self.pk])


class AWSLoadBalancer(NetBoxModel):
    name = models.CharField(max_length=255, help_text="The name of the Load Balancer")
    arn = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="ARN",
        help_text="Amazon Resource Name for the Load Balancer",
    )
    aws_account = models.ForeignKey(
        to=AWSAccount,
        on_delete=models.PROTECT,
        related_name="account_load_balancers",
        help_text="The AWS Account this Load Balancer belongs to",
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the Load Balancer is located"
    )
    vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="vpc_load_balancers",
        help_text="The VPC this Load Balancer is associated with. Region is derived from this VPC.",
    )
    type = models.CharField(
        max_length=50,
        choices=LOADBALANCER_TYPE_CHOICES,
        help_text="The type of Load Balancer (e.g., application, network, gateway)",
    )
    scheme = models.CharField(
        max_length=50,
        choices=LOADBALANCER_SCHEME_CHOICES,
        help_text="The scheme of the Load Balancer (e.g., internet-facing, internal)",
    )
    dns_name = models.CharField(
        max_length=255, blank=True, verbose_name="DNS Name", help_text="The DNS name of the Load Balancer"
    )
    state = models.CharField(
        max_length=50,
        choices=LOADBALANCER_STATE_CHOICES,
        help_text="The state of the Load Balancer (e.g., active, provisioning, failed)",
    )
    subnets = models.ManyToManyField(
        to=AWSSubnet,
        related_name="load_balancers",
        blank=True,
        help_text="Subnets associated with this Load Balancer. Should be within the selected VPC.",
    )

    class Meta:
        ordering = ("name",)


# Choices for EC2 Instance model fields
RDS_INSTANCE_STATE_CHOICES = [
    ("available", "Available"),
    ("creating", "Creating"),
    ("deleting", "Deleting"),
    ("failed", "Failed"),
    ("inaccessible-encryption-credentials", "Inaccessible Encryption Credentials"),
    ("modifying", "Modifying"),
    ("rebooting", "Rebooting"),
    ("renaming", "Renaming"),
    ("starting", "Starting"),
    ("stopped", "Stopped"),
    ("stopping", "Stopping"),
    ("storage-full", "Storage Full"),
    ("upgrading", "Upgrading"),
]

# Choices for EC2 Instance model fields
EC2_INSTANCE_STATE_CHOICES = [
    ("pending", "Pending"),
    ("running", "Running"),
    ("shutting-down", "Shutting Down"),
    ("terminated", "Terminated"),
    ("stopping", "Stopping"),
    ("stopped", "Stopped"),
]


class AWSTargetGroup(NetBoxModel):
    name = models.CharField(max_length=255, help_text="The name of the Target Group")
    arn = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="ARN",
        help_text="Amazon Resource Name for the Target Group",
    )
    aws_account = models.ForeignKey(
        to=AWSAccount,
        on_delete=models.PROTECT,
        related_name="target_groups",
        help_text="The AWS Account this Target Group belongs to",
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the Target Group is located"
    )
    vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="target_groups",
        help_text="The VPC this Target Group is associated with. Region is derived from this VPC.",
    )
    service = models.ForeignKey(
        to=Service,
        on_delete=models.PROTECT,
        related_name="aws_target_groups",
        blank=True,
        null=True,
        help_text="Service (port and protocol) associated with this Target Group",
    )
    target_type = models.CharField(
        max_length=10,
        choices=TARGET_GROUP_TYPE_CHOICES,
        verbose_name="Target Type",
        help_text="Type of targets (instance, ip, alb)",
    )
    load_balancers = models.ManyToManyField(
        to=AWSLoadBalancer,
        related_name="target_groups",
        blank=True,
        help_text="Load Balancers associated with this Target Group",
    )
    # Health Check Settings
    health_check_protocol = models.CharField(
        max_length=10,
        choices=TARGET_GROUP_HEALTH_CHECK_PROTOCOL_CHOICES,
        blank=True,
        null=True,
        verbose_name="Health Check Protocol",
        help_text="Protocol for health checks",
    )
    health_check_port = models.CharField(
        max_length=20,
        default="traffic-port",
        blank=True,
        null=True,
        verbose_name="Health Check Port",
        help_text="Port for health checks (default: 'traffic-port')",
    )
    health_check_path = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Health Check Path",
        help_text="Destination for HTTP/HTTPS health checks",
    )
    health_check_interval_seconds = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Health Check Interval Seconds",
        help_text="Approximate interval between health checks (seconds)",
    )
    health_check_timeout_seconds = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Health Check Timeout Seconds",
        help_text="Timeout for a health check response (seconds)",
    )
    healthy_threshold_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Healthy Threshold Count",
        help_text="Number of consecutive successful health checks to become healthy",
    )
    unhealthy_threshold_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Unhealthy Threshold Count",
        help_text="Number of consecutive failed health checks to become unhealthy",
    )
    state = models.CharField(
        max_length=30,
        choices=AWS_TARGET_GROUP_STATE_CHOICES,
        default="active",
        help_text="The current state of the Target Group",
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # TODO: Update when AWSTargetGroup view is created
        return reverse("plugins:netbox_aws_resources_plugin:awsloadbalancer_list")  # Placeholder

    def save(self, *args, **kwargs):
        # VPC is now mandatory, so self.vpc will always be set.
        self.region = self.vpc.region
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        verbose_name = "AWS Target Group"
        verbose_name_plural = "AWS Target Groups"


class AWSEC2Instance(NetBoxModel):
    name = models.CharField(max_length=255, help_text="The name of the EC2 Instance")
    instance_id = models.CharField(
        max_length=24,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Instance ID",
        help_text="The unique ID of the EC2 Instance",
    )
    aws_account = models.ForeignKey(
        to=AWSAccount,
        on_delete=models.PROTECT,
        related_name="ec2_instances",
        help_text="The AWS Account this EC2 Instance belongs to",
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the EC2 Instance is located"
    )
    vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="ec2_instances",
        help_text="The VPC this EC2 Instance is associated with.",
    )
    subnet = models.ForeignKey(
        to=AWSSubnet,
        on_delete=models.PROTECT,
        related_name="ec2_instances",
        help_text="The Subnet this EC2 Instance is associated with.",
        blank=True,
        null=True,
    )
    instance_type = models.CharField(
        max_length=255, blank=True, help_text="The type of the EC2 instance (e.g. t2.micro)"
    )
    state = models.CharField(
        max_length=30, choices=EC2_INSTANCE_STATE_CHOICES, blank=True, help_text="The current state of the EC2 Instance"
    )
    estimated_cost_usd_hourly = models.DecimalField(
        max_digits=10, decimal_places=5, null=True, blank=True, verbose_name="Estimated Hourly Cost (USD)"
    )
    # Link to NetBox's VirtualMachine model
    virtual_machine = models.OneToOneField(
        to=VirtualMachine, on_delete=models.SET_NULL, related_name="aws_ec2_instance", blank=True, null=True
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "AWS EC2 Instance"
        verbose_name_plural = "AWS EC2 Instances"

    def __str__(self):
        return self.name or self.instance_id

    def get_absolute_url(self):
        # TODO: Create a view for AWSEC2Instance
        return reverse("plugins:netbox_aws_resources_plugin:awsaccount_list")  # Placeholder

    def save(self, *args, **kwargs):
        specs = None
        # If an instance type is set, try to find its specs to update cost and VM details.
        if self.instance_type:
            try:
                data_file = Path(__file__).parent / "data" / "instance_data.json"
                with open(data_file, "r") as f:
                    instance_data = json.load(f)
                specs = instance_data.get("ec2", {}).get(self.instance_type)
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                specs = None  # Ensure specs is None if file/key is missing

        # If we found specs, update the cost on this instance.
        if specs:
            self.estimated_cost_usd_hourly = specs.get("price_usd_hourly")

        # Save the AWSEC2Instance itself.
        super().save(*args, **kwargs)

        # After saving, if a VM is linked and we have specs, update the VM.
        if self.virtual_machine and specs:
            vm_updated = False

            new_vcpus = specs.get("vcpu")
            new_ram_gb = specs.get("ram_gb")

            if new_vcpus is not None and self.virtual_machine.vcpus != new_vcpus:
                self.virtual_machine.vcpus = new_vcpus
                vm_updated = True

            if new_ram_gb is not None:
                memory_mb = new_ram_gb * 1024
                if self.virtual_machine.memory != memory_mb:
                    self.virtual_machine.memory = memory_mb
                    vm_updated = True

            if vm_updated:
                self.virtual_machine.save()


class AWSRDSInstance(NetBoxModel):
    name = models.CharField(max_length=255, help_text="The name of the RDS Instance")
    instance_id = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name="DB Identifier",
        help_text="The unique identifier for the RDS instance",
    )
    aws_account = models.ForeignKey(
        to=AWSAccount,
        on_delete=models.PROTECT,
        related_name="rds_instances",
        help_text="The AWS Account this RDS Instance belongs to",
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the RDS Instance is located"
    )
    vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="rds_instances",
        help_text="The VPC this RDS Instance is associated with.",
    )
    subnet = models.ForeignKey(
        to=AWSSubnet,
        on_delete=models.PROTECT,
        related_name="rds_instances",
        help_text="The Subnet this RDS Instance is associated with.",
        blank=True,
        null=True,
    )
    instance_class = models.CharField(
        max_length=255, blank=True, help_text="The compute and memory capacity of the DB instance (e.g., db.t3.micro)"
    )
    engine = models.CharField(
        max_length=50,
        blank=True,
        help_text="The name of the database engine to be used for this instance (e.g., postgres, mysql)",
    )
    engine_version = models.CharField(max_length=50, blank=True, help_text="The version number of the database engine")
    state = models.CharField(
        max_length=50, choices=RDS_INSTANCE_STATE_CHOICES, blank=True, help_text="The current state of the RDS Instance"
    )
    estimated_cost_usd_hourly = models.DecimalField(
        max_digits=10, decimal_places=5, null=True, blank=True, verbose_name="Estimated Hourly Cost (USD)"
    )
    # Link to NetBox's VirtualMachine model
    virtual_machine = models.OneToOneField(
        to=VirtualMachine, on_delete=models.SET_NULL, related_name="aws_rds_instance", blank=True, null=True
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "AWS RDS Instance"
        verbose_name_plural = "AWS RDS Instances"

    def __str__(self):
        return self.name or self.instance_id

    def get_absolute_url(self):
        # TODO: Create a view for AWSRDSInstance
        return reverse("plugins:netbox_aws_resources_plugin:awsaccount_list")  # Placeholder

    def save(self, *args, **kwargs):
        specs = None
        # If an instance class is set, try to find its specs to update cost and VM details.
        if self.instance_class:
            try:
                data_file = Path(__file__).parent / "data" / "instance_data.json"
                with open(data_file, "r") as f:
                    instance_data = json.load(f)
                specs = instance_data.get("rds", {}).get(self.instance_class)
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                specs = None  # Ensure specs is None if file/key is missing

        # If we found specs, update the cost on this instance.
        if specs:
            self.estimated_cost_usd_hourly = specs.get("price_usd_hourly")

        # Save the AWSRDSInstance itself.
        super().save(*args, **kwargs)

        # After saving, if a VM is linked and we have specs, update the VM.
        if self.virtual_machine and specs:
            vm_updated = False

            new_vcpus = specs.get("vcpu")
            new_ram_gb = specs.get("ram_gb")

            if new_vcpus is not None and self.virtual_machine.vcpus != new_vcpus:
                self.virtual_machine.vcpus = new_vcpus
                vm_updated = True

            if new_ram_gb is not None:
                memory_mb = new_ram_gb * 1024
                if self.virtual_machine.memory != memory_mb:
                    self.virtual_machine.memory = memory_mb
                    vm_updated = True

            if vm_updated:
                self.virtual_machine.save()
