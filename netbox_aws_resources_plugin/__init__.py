"""Top-level package for NetBox AWS Resources Plugin."""

__author__ = """Jordan Keith"""
__email__ = "jordan@iopc.com.au"
__version__ = "4.0.0-alpha1"


from netbox.plugins import PluginConfig


class AWSResourcesConfig(PluginConfig):
    name = "netbox_aws_resources_plugin"
    verbose_name = "NetBox AWS Resources Plugin"
    description = "NetBox plugin for AWS Resources."
    version = __version__
    base_url = "netbox-aws-resources-plugin"
    author = __author__
    author_email = __email__
    default_settings = {"api_version": "2.0"}  # Or the appropriate API version for your Netbox version
    # Explicitly define the app_name for the API URLs
    api_app_name = "netbox_aws_resources_plugin-api"


config = AWSResourcesConfig
