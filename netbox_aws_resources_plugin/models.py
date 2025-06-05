from django.db import models
from django.urls import reverse
from ipam.models import Prefix  # Import NetBox Prefix model
from netbox.models import NetBoxModel
from tenancy.models import Tenant


class AWSAccount(NetBoxModel):
    account_id = models.CharField(max_length=12, unique=True, help_text="AWS Account ID (12 digits)", blank=True, null=True)
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


# Choices for LoadBalancer model fields
AWS_REGION_CHOICES = [
    ("us-east-1", "US East (N. Virginia)"),
    ("us-east-2", "US East (Ohio)"),
    ("us-west-1", "US West (N. California)"),
    ("us-west-2", "US West (Oregon)"),
    ("ap-northeast-1", "Asia Pacific (Tokyo)"),
    ("ap-northeast-2", "Asia Pacific (Seoul)"),
    ("ap-southeast-1", "Asia Pacific (Singapore)"),
    ("ap-southeast-2", "Asia Pacific (Sydney)"),
    ("ca-central-1", "Canada (Central)"),
    ("eu-central-1", "Europe (Frankfurt)"),
    ("eu-west-1", "Europe (Ireland)"),
    ("eu-west-2", "Europe (London)"),
    ("eu-north-1", "Europe (Stockholm)"),
    ("sa-east-1", "South America (São Paulo)"),
]

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
    ('planned', 'Planned'),
    ("active", "Active"),
    ("provisioning", "Provisioning"),
    ("active_impaired", "Active Impaired"),
    ("failed", "Failed"),
    ("unknown", "Unknown"),
]

AWS_VPC_STATE_CHOICES = [
    ('planned', 'Planned'),
    ("pending", "Pending"),
    ("available", "Available"),
]

AWS_SUBNET_STATE_CHOICES = [
    ('planned', 'Planned'),
    ("pending", "Pending"),
    ("available", "Available"),
]

# Choices for TargetGroup model fields
TARGET_GROUP_PROTOCOL_CHOICES = [
    ('HTTP', 'HTTP'),
    ('HTTPS', 'HTTPS'),
    ('TCP', 'TCP'),
    ('TLS', 'TLS'),
    ('UDP', 'UDP'),
    ('TCP_UDP', 'TCP_UDP'),
    ('GENEVE', 'GENEVE'),
]

TARGET_GROUP_TYPE_CHOICES = [
    ('instance', 'EC2 Instance'),
    ('ip', 'IP Address'),
    # ('lambda', 'Lambda function'), # Lambda targets are not supported by this plugin model
    ('alb', 'Application Load Balancer'),
]

TARGET_GROUP_HEALTH_CHECK_PROTOCOL_CHOICES = [
    ('HTTP', 'HTTP'),
    ('HTTPS', 'HTTPS'),
    ('TCP', 'TCP'),
]

AWS_TARGET_GROUP_STATE_CHOICES = [
    ('planned', 'Planned'),
    ('creating', 'Creating'),
    ('active', 'Active'),
    ('deleting', 'Deleting'),
    ('failed', 'Failed'),
]


class AWSVPC(NetBoxModel):
    aws_account = models.ForeignKey(
        to=AWSAccount,
        on_delete=models.PROTECT,
        related_name="vpcs",
        help_text="The AWS Account this VPC belongs to"
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
            related_name="aws_vpc_primary_cidr", # Ensure this related_name is unique if used elsewhere
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

    def __str__(self):
        return self.name or self.vpc_id

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_resources_plugin:awsvpc", args=[self.pk])


class AWSSubnet(NetBoxModel):
    aws_vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="subnets",
        help_text="The AWS VPC this Subnet belongs to"
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
        max_length=50, blank=True, help_text="The Availability Zone of the Subnet (e.g., us-east-1a)"
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
        default=False, help_text="Whether instances in this subnet get a public IP on launch by default"
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
    arn = models.CharField(max_length=255, unique=True, blank=True, verbose_name="ARN", help_text="Amazon Resource Name for the Load Balancer")
    aws_account = models.ForeignKey(
        to=AWSAccount, on_delete=models.PROTECT, related_name="account_load_balancers", help_text="The AWS Account this Load Balancer belongs to"
    )
    region = models.CharField(max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the Load Balancer is located")
    vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="vpc_load_balancers",
        help_text="The VPC this Load Balancer is associated with. Region is derived from this VPC.",
    )
    type = models.CharField(max_length=50, choices=LOADBALANCER_TYPE_CHOICES, help_text="The type of Load Balancer (e.g., application, network, gateway)")
    scheme = models.CharField(max_length=50, choices=LOADBALANCER_SCHEME_CHOICES, help_text="The scheme of the Load Balancer (e.g., internet-facing, internal)")
    dns_name = models.CharField(max_length=255, blank=True, help_text="The DNS name of the Load Balancer")
    state = models.CharField(max_length=50, choices=LOADBALANCER_STATE_CHOICES, help_text="The state of the Load Balancer (e.g., active, provisioning, failed)")
    subnets = models.ManyToManyField(
        to=AWSSubnet,
        related_name="load_balancers",
        blank=True,
        help_text="Subnets associated with this Load Balancer. Should be within the selected VPC."
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_aws_resources_plugin:awsloadbalancer", args=[self.pk])

    def save(self, *args, **kwargs):
        # VPC is now mandatory, so self.vpc will always be set.
        self.region = self.vpc.region
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)


class AWSTargetGroup(NetBoxModel):
    name = models.CharField(max_length=255, help_text="The name of the Target Group")
    arn = models.CharField(max_length=255, unique=True, blank=True, null=True, verbose_name="ARN", help_text="Amazon Resource Name for the Target Group")
    aws_account = models.ForeignKey(
        to=AWSAccount, on_delete=models.PROTECT, related_name="target_groups", help_text="The AWS Account this Target Group belongs to"
    )
    region = models.CharField(max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the Target Group is located")
    vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.PROTECT,
        related_name="target_groups",
        help_text="The VPC this Target Group is associated with. Region is derived from this VPC.",
    )
    protocol = models.CharField(max_length=10, choices=TARGET_GROUP_PROTOCOL_CHOICES, help_text="Protocol for routing traffic to targets")
    port = models.PositiveIntegerField(help_text="Port on which targets receive traffic")
    target_type = models.CharField(max_length=10, choices=TARGET_GROUP_TYPE_CHOICES, help_text="Type of targets (instance, ip, alb)")
    load_balancers = models.ManyToManyField(
        to=AWSLoadBalancer,
        related_name="target_groups",
        blank=True,
        help_text="Load Balancers associated with this Target Group"
    )
    # Health Check Settings
    health_check_protocol = models.CharField(
        max_length=10, choices=TARGET_GROUP_HEALTH_CHECK_PROTOCOL_CHOICES, blank=True, null=True, help_text="Protocol for health checks"
    )
    health_check_port = models.CharField(
        max_length=20, default='traffic-port', blank=True, null=True, help_text="Port for health checks (default: 'traffic-port')"
    )
    health_check_path = models.CharField(max_length=255, blank=True, null=True, help_text="Destination for HTTP/HTTPS health checks")
    health_check_interval_seconds = models.PositiveIntegerField(blank=True, null=True, help_text="Approximate interval between health checks (seconds)")
    health_check_timeout_seconds = models.PositiveIntegerField(blank=True, null=True, help_text="Timeout for a health check response (seconds)")
    healthy_threshold_count = models.PositiveIntegerField(blank=True, null=True, help_text="Number of consecutive successful health checks to become healthy")
    unhealthy_threshold_count = models.PositiveIntegerField(blank=True, null=True, help_text="Number of consecutive failed health checks to become unhealthy")
    state = models.CharField(max_length=30, choices=AWS_TARGET_GROUP_STATE_CHOICES, default='active', help_text="The current state of the Target Group")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # TODO: Update when AWSTargetGroup view is created
        return reverse("plugins:netbox_aws_resources_plugin:awsloadbalancer_list") # Placeholder

    def save(self, *args, **kwargs):
        # VPC is now mandatory, so self.vpc will always be set.
        self.region = self.vpc.region
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("name",)
        verbose_name = "AWS Target Group"
        verbose_name_plural = "AWS Target Groups"
