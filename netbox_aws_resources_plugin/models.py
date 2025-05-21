from django.db import models
from django.urls import reverse
from ipam.models import Prefix  # Import NetBox Prefix model
from netbox.models import NetBoxModel
from tenancy.models import Tenant


class AWSAccount(NetBoxModel):
    account_id = models.CharField(max_length=12, unique=True, help_text="AWS Account ID (12 digits)")
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
    ("active", "Active"),
    ("provisioning", "Provisioning"),
    ("active_impaired", "Active Impaired"),
    ("failed", "Failed"),
    ("unknown", "Unknown"),
]

AWS_VPC_STATE_CHOICES = [
    ("pending", "Pending"),
    ("available", "Available"),
]

AWS_SUBNET_STATE_CHOICES = [
    ("pending", "Pending"),
    ("available", "Available"),
]


class AWSVPC(NetBoxModel):
    name = models.CharField(
        max_length=255,
        blank=True,  # Name is optional in AWS, can be derived from tags
        help_text="User-defined name for the VPC",
    )
    vpc_id = models.CharField(
        max_length=50,  # e.g., vpc-012345abcdef1234567
        unique=True,
        verbose_name="VPC ID",
        help_text="The unique identifier for the VPC (e.g., vpc-012345abcdef)",
    )
    aws_account = models.ForeignKey(
        to=AWSAccount, on_delete=models.PROTECT, related_name="vpcs", help_text="The AWS Account this VPC belongs to"
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the VPC is located"
    )
    # Represents the primary IPv4 CIDR block. Additional CIDR blocks are handled via ipam.Prefix relationships if needed
    cidr_block = (
        models.OneToOneField(  # A VPC has one primary CIDR block in AWS, often represented as a Prefix in NetBox
            to=Prefix,
            on_delete=models.PROTECT,  # Protecting the Prefix if a VPC references it
            related_name="aws_vpc_primary_cidr",
            null=True,  # Can be null if not yet provisioned or if managed differently
            blank=True,
            help_text="The primary IPv4 CIDR block of this VPC, represented as a NetBox Prefix",
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
    name = models.CharField(
        max_length=255,
        blank=True,  # Name is optional in AWS, can be derived from tags
        help_text="User-defined name for the Subnet",
    )
    subnet_id = models.CharField(
        max_length=50,  # e.g., subnet-012345abcdef1234567
        unique=True,
        verbose_name="Subnet ID",
        help_text="The unique identifier for the Subnet (e.g., subnet-012345abcdef)",
    )
    aws_vpc = models.ForeignKey(
        to=AWSVPC,
        on_delete=models.CASCADE,  # Subnets are deleted if their VPC is deleted
        related_name="subnets",
        help_text="The AWS VPC this Subnet belongs to",
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
    arn = models.CharField(max_length=255, unique=True, help_text="Amazon Resource Name (ARN) of the Load Balancer")
    aws_account = models.ForeignKey(
        to=AWSAccount,
        on_delete=models.PROTECT,  # Or models.CASCADE if LBs should be deleted with account
        related_name="load_balancers",
        help_text="The AWS Account this Load Balancer belongs to",
    )
    region = models.CharField(
        max_length=50, choices=AWS_REGION_CHOICES, help_text="The AWS region where the Load Balancer is located"
    )
    vpc = models.ForeignKey(
        to=AWSVPC,  # Changed from ipam.VPC to AWSVPC
        on_delete=models.SET_NULL,  # Or models.PROTECT
        null=True,
        blank=True,
        related_name="aws_load_balancers",  # Keep or change related_name as preferred
        help_text="The AWS VPC this Load Balancer is associated with (optional)",
    )
    type = models.CharField(
        max_length=20,
        choices=LOADBALANCER_TYPE_CHOICES,
        help_text="The type of Load Balancer (Application, Network, Gateway)",
    )
    scheme = models.CharField(
        max_length=20,
        choices=LOADBALANCER_SCHEME_CHOICES,
        help_text="The scheme of the Load Balancer (internal or internet-facing)",
    )
    dns_name = models.CharField(
        max_length=255,
        blank=True,  # Can be blank as it might take time to provision
        help_text="The DNS name of the Load Balancer",
    )
    state = models.CharField(
        max_length=20,
        choices=LOADBALANCER_STATE_CHOICES,
        default="unknown",
        help_text="The current state of the Load Balancer",
    )

    class Meta:
        ordering = ("name", "region", "aws_account")
        verbose_name = "AWS Load Balancer"
        verbose_name_plural = "AWS Load Balancers"
        constraints = [
            models.UniqueConstraint(
                fields=["aws_account", "region", "name"], name="unique_awsloadbalancer_account_region_name"
            )
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # Placeholder: URL will be defined in urls.py later
        return reverse("plugins:netbox_aws_resources_plugin:awsloadbalancer", args=[self.pk])
