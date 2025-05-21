from netbox.search import SearchIndex, register_search

from .models import AWSAccount


@register_search
class AWSAccountIndex(SearchIndex):
    model = AWSAccount

    fields = (
        ("account_id", 1000),
        ("name", 1000),
        ("search_parent_name", 1100),  # Use property from model
        ("search_parent_account_id", 1100),  # Use property from model
    )

    display_attrs = (
        "account_id",
        "name",
        "tenant",
        "parent_account",
    )
