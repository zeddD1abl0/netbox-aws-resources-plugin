from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

plugin_buttons = [
    PluginMenuButton(
        link="plugins:netbox_aws_resources_plugin:awsresources_add",
        title="Add",
        icon_class="mdi mdi-plus-thick",
    )
]

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_aws_resources_plugin:awsresources_list",
        link_text="AWS Resources",
        buttons=plugin_buttons,
    ),
)
