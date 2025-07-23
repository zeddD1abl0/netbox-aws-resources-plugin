from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

# Button for adding a new AWS Account
awsaccount_add_button = PluginMenuButton(
    link="plugins:netbox_aws_resources_plugin:awsaccount_add",
    title="Add Account",
    icon_class="mdi mdi-plus-thick",
    color=ButtonColorChoices.GREEN,
)

# Button for adding a new AWS VPC
awsvpc_add_button = PluginMenuButton(
    link="plugins:netbox_aws_resources_plugin:awsvpc_add",
    title="Add VPC",
    icon_class="mdi mdi-plus-thick",
    color=ButtonColorChoices.GREEN,
)

# Button for adding a new AWS Subnet
awssubnet_add_button = PluginMenuButton(
    link="plugins:netbox_aws_resources_plugin:awssubnet_add",
    title="Add Subnet",
    icon_class="mdi mdi-plus-thick",
    color=ButtonColorChoices.GREEN,
)

# Button for adding a new AWS Load Balancer
awsloadbalancer_add_button = PluginMenuButton(
    link="plugins:netbox_aws_resources_plugin:awsloadbalancer_add",
    title="Add Load Balancer",
    icon_class="mdi mdi-plus-thick",
    color=ButtonColorChoices.GREEN,
)

# Button for adding a new AWS Target Group
awstargetgroup_add_button = PluginMenuButton(
    link="plugins:netbox_aws_resources_plugin:awstargetgroup_add",
    title="Add Target Group",
    icon_class="mdi mdi-plus-thick",
    color=ButtonColorChoices.GREEN,
)

# Button for adding a new AWS EC2 Instance
awsec2instance_add_button = PluginMenuButton(
    link="plugins:netbox_aws_resources_plugin:awsec2instance_add",
    title="Add EC2 Instance",
    icon_class="mdi mdi-plus-thick",
    color=ButtonColorChoices.GREEN,
)

# Menu item for listing AWS Accounts
awsaccount_list_item = PluginMenuItem(
    link="plugins:netbox_aws_resources_plugin:awsaccount_list",
    link_text="AWS Accounts",
    buttons=(awsaccount_add_button,),
)

# Menu item for listing AWS VPCs
awsvpc_list_item = PluginMenuItem(
    link="plugins:netbox_aws_resources_plugin:awsvpc_list",
    link_text="AWS VPCs",
    buttons=(awsvpc_add_button,),
)

# Menu item for listing AWS Subnets
awssubnet_list_item = PluginMenuItem(
    link="plugins:netbox_aws_resources_plugin:awssubnet_list",
    link_text="AWS Subnets",
    buttons=(awssubnet_add_button,),
)

# Menu item for listing AWS Load Balancers
awsloadbalancer_list_item = PluginMenuItem(
    link="plugins:netbox_aws_resources_plugin:awsloadbalancer_list",
    link_text="AWS Load Balancers",
    buttons=(awsloadbalancer_add_button,),
)

# Menu item for listing AWS Target Groups
awstargetgroup_list_item = PluginMenuItem(
    link="plugins:netbox_aws_resources_plugin:awstargetgroup_list",
    link_text="AWS Target Groups",
    buttons=(awstargetgroup_add_button,)
)

# Menu item for listing AWS EC2 Instances
awsec2instance_list_item = PluginMenuItem(
    link="plugins:netbox_aws_resources_plugin:awsec2instance_list",
    link_text="AWS EC2 Instances",
    buttons=(awsec2instance_add_button,)
)

# Define the top-level menu
menu = PluginMenu(
    label="AWS Resources",  # Text that will appear on the top-level tab
    groups=(
        ("AWS Management", (awsaccount_list_item, awsvpc_list_item, awssubnet_list_item, awsloadbalancer_list_item, awstargetgroup_list_item, awsec2instance_list_item)),
        # You can add more groups and items here later as your plugin grows
    ),
    icon_class="mdi mdi-cloud",  # Original cloud icon
)
