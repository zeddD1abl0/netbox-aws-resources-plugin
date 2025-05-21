# NetBox AWS Resources Plugin

NetBox plugin for discovering and managing various AWS Resources within NetBox. This plugin aims to provide visibility into your AWS infrastructure and its relationship with your on-premises or other cloud resources tracked in NetBox.


* Free software: Apache-2.0
* Documentation: https://zeddD1abl0.github.io/netbox-aws-resources-plugin/


## Features

Currently, the plugin provides the following features, primarily focused on AWS Account management:

*   **AWS Account Tracking:**
    *   Store AWS Account ID (12-digit), a descriptive Name, and associate with a NetBox Tenant.
    *   Support for hierarchical relationships using a `Parent Account` field, allowing for representation of AWS Organizations structures or other parent-child account relationships.
*   **User Interface Enhancements:**
    *   Dedicated list view for AWS Accounts with custom columns like "Account Type" (Root/Sub-account) and "Parent Account".
    *   Filtering options, including a specific filter for "Is Root Account" (Yes/No/Any).
    *   Detailed AWS Account page displaying parent account information and a table of any child accounts.
*   **Bulk Operations:**
    *   Bulk editing of AWS Accounts.
    *   Bulk deletion of AWS Accounts.
*   **Search Integration:**
    *   AWS Accounts (including their ID, name, and tenant) are searchable via NetBox's global search.
    *   Ability to find child accounts by searching for their parent account's ID or name.

**Future planned features include support for:**
*   AWS Load Balancers (ALB/NLB)
*   Target Groups
*   ECS Clusters, Services, and Tasks

## Models

### AWSAccount

Represents an individual AWS Account.

*   **`account_id`**: The unique 12-digit AWS Account ID.
*   **`name`**: A user-defined descriptive name for the account.
*   **`tenant`**: The NetBox Tenant this AWS Account is associated with (optional).
*   **`parent_account`**: A foreign key to another `AWSAccount` instance, representing the parent in a hierarchy. If null, the account is considered a "Root" account.

## Compatibility

| NetBox Version | Plugin Version |
|----------------|----------------|
|     4.0        |      0.1.0     |

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
