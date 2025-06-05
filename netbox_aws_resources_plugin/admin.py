from django.contrib import admin

from .models import AWSAccount, AWSVPC, AWSSubnet, AWSLoadBalancer, AWSTargetGroup


@admin.register(AWSAccount)
class AWSAccountAdmin(admin.ModelAdmin):
    list_display = ("account_id", "name", "tenant")
    list_filter = ("tenant",)
    search_fields = ("account_id", "name")


@admin.register(AWSVPC)
class AWSVPCAdmin(admin.ModelAdmin):
    list_display = ("name", "vpc_id", "aws_account", "region", "state")
    list_filter = ("aws_account", "region", "state")
    search_fields = ("name", "vpc_id")


@admin.register(AWSSubnet)
class AWSSubnetAdmin(admin.ModelAdmin):
    list_display = ("name", "subnet_id", "aws_vpc", "availability_zone", "state")
    list_filter = ("aws_vpc__aws_account", "aws_vpc__region", "availability_zone", "state")
    search_fields = ("name", "subnet_id")


@admin.register(AWSLoadBalancer)
class AWSLoadBalancerAdmin(admin.ModelAdmin):
    list_display = ("name", "aws_account", "region", "type", "scheme", "state")
    list_filter = ("aws_account", "region", "type", "scheme", "state")
    search_fields = ("name", "arn", "dns_name")


@admin.register(AWSTargetGroup)
class AWSTargetGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "aws_account", "region", "protocol", "port", "target_type", "state")
    list_filter = ("aws_account", "region", "protocol", "target_type", "state")
    search_fields = ("name", "arn")
