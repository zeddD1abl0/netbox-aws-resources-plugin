"""Top-level package for NetBox AWS Resources Plugin."""

__author__ = """Jordan Keith"""
__email__ = "jordan@iopc.com.au"
__version__ = "0.1.0"


from netbox.plugins import PluginConfig


class AWSResourcesConfig(PluginConfig):
    name = "netbox_aws_resources_plugin"
    verbose_name = "NetBox AWS Resources Plugin"
    description = "NetBox plugin for AWS Resources."
    version = "version"
    base_url = "netbox_aws_resources_plugin"


config = AWSResourcesConfig
