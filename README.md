# NetBox AWS Resources Plugin

* Free software: Apache-2.0
* Documentation: https://zeddD1abl0.github.io/netbox-aws-resources-plugin/

A plugin for NetBox to model and manage Amazon Web Services (AWS) resources. This plugin extends NetBox to serve as a source of truth for key AWS infrastructure components, enabling better visibility and management of your cloud and on-premise resources in one place.

## Features

This plugin introduces the following models to NetBox:

*   **AWS Account**: Manage AWS account information, including Account ID and parent/child relationships for AWS Organizations.
*   **AWS VPC**: Model your Virtual Private Clouds, including their CIDR blocks and region.
*   **AWS Subnet**: Track your VPC subnets, their CIDR blocks, and availability zones.
*   **AWS EC2 Instance**: Document your EC2 instances, including instance type, VPC/subnet placement, and link them to NetBox Virtual Machines.
*   **AWS RDS Instance**: Keep track of your RDS database instances, their class, engine, and VPC/subnet placement.
*   **AWS Load Balancer**: Model Application, Network, and Gateway Load Balancers, their type, scheme, and associated subnets.
*   **AWS Target Group**: Define Target Groups for your load balancers, linking them to a specific NetBox Service (protocol and port).

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

## Installation

For adding to a NetBox Docker setup see
[the general instructions for using netbox-docker with plugins](https://github.com/netbox-community/netbox-docker/wiki/Using-Netbox-Plugins).

While this is still in development and not yet on pypi you can install with pip from the root of this repository:

```bash
pip install .
```

Alternatively, you can install with pip from git:

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

After installing the plugin, run the following commands from the NetBox root directory (`/opt/netbox/netbox/`):

```bash
# Apply database migrations
./manage.py migrate

# Collect static files
./manage.py collectstatic

# Restart NetBox services
sudo systemctl restart netbox netbox-rq
```

## Usage

Once installed and configured, you will find an "AWS" section in the NetBox navigation menu. From there, you can add and manage your AWS resources just like any other NetBox object.

## Credits

Based on the NetBox plugin tutorial:

- [demo repository](https://github.com/netbox-community/netbox-plugin-demo)
- [tutorial](https://github.com/netbox-community/netbox-plugin-tutorial)

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [`netbox-community/cookiecutter-netbox-plugin`](https://github.com/netbox-community/cookiecutter-netbox-plugin) project template.
