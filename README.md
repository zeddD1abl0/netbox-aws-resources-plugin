# NetBox AWS Resources Plugin

NetBox plugin for discovering and managing various AWS Resources within NetBox. This plugin aims to provide visibility into your AWS infrastructure and its relationship with your on-premises or other cloud resources tracked in NetBox.


* Free software: Apache-2.0
* Documentation: https://zeddD1abl0.github.io/netbox-aws-resources-plugin/


## Features

Currently, the plugin provides the following features, focused on AWS resource management:

*   **AWS Account Tracking:**
    *   Store AWS Account ID (12-digit), a descriptive Name, and associate with a NetBox Tenant.
    *   Support for hierarchical relationships using a `Parent Account` field, allowing for representation of AWS Organizations structures or other parent-child account relationships.
*   **AWS VPC Management:**
    *   Store VPC ID, a descriptive Name, CIDR block (linked to `ipam.Prefix`), and associate with an AWS Account and NetBox Tenant.
*   **AWS Subnet Management:**
    *   Store Subnet ID, a descriptive Name, CIDR block (linked to `ipam.Prefix`), Availability Zone, and associate with an AWS VPC and NetBox Tenant.
*   **AWS Load Balancer Management (ALB/NLB):**
    *   Store Load Balancer ARN, Name, Type (Application/Network), Scheme (Internal/Internet-facing), DNS Name, and associate with an AWS Account, VPC, and NetBox Tenant.
    *   Track associated Subnets.
*   **User Interface Enhancements:**
    *   Dedicated list views for AWS Accounts, VPCs, Subnets, and Load Balancers with relevant custom columns.
    *   Filtering options for all managed resources.
    *   Detailed pages for each resource displaying its attributes and related items (e.g., VPCs under an Account, Subnets under a VPC, Load Balancers under an Account/VPC).
*   **Bulk Operations:**
    *   Bulk editing and deletion for all managed resources.
*   **Search Integration:**
    *   All managed AWS resources are searchable via NetBox's global search.

**Future planned features include support for:**
*   Target Groups

## Models

The plugin introduces the following NetBox models. For detailed information on each model, please refer to the documentation links below:

*   [AWSAccount](./docs/models/aws_account.md)
*   [AWSVPC](./docs/models/aws_vpc.md)
*   [AWSSubnet](./docs/models/aws_subnet.md)
*   [AWSLoadBalancer](./docs/models/aws_load_balancer.md)

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.0        |   4.0.0-alpha1 |

## Installing

For adding to a NetBox Docker setup see
[the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

While this is still in development and not yet on pypi you can install with pip:

```bash
pip install git+https://github.com/zeddD1abl0/netbox-aws-resources-plugin
```

or by adding to your `local_requirements.txt` or `plugin_requirements.txt` (netbox-docker):

```bash
git+https://github.com/zeddD1abl0/netbox-aws-resources-plugin
```

Enable the plugin in `/opt/netbox/netbox/netbox/configuration.py`,
 or if you use netbox-docker, your `/configuration/plugins.py` file :

```python
PLUGINS = [
    'netbox_aws_resources_plugin' # Ensure this matches your plugin's package name
]

PLUGINS_CONFIG = {
    "netbox_aws_resources_plugin": { # Ensure this matches your plugin's package name
        # Plugin-specific configuration options can be added here in the future
    },
}
```

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
