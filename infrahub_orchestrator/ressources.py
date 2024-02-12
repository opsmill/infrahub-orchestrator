from dagster import (
    Field,
    String,
    resource,
)
from infrahub_sync.utils import get_instance, get_potenda_from_instance
from potenda import Potenda


@resource(
    config_schema={
        "name": Field(String),
        "branch": Field(String, default_value="main", is_required=False),
        "show_progress": Field(bool, default_value=False, is_required=False),
    },
)
def sync_instance(init_context) -> Potenda:
    name = init_context.resource_config["name"]
    branch = init_context.resource_config.get("branch", "main")
    show_progress = init_context.resource_config.get("show_progress", False)
    sync_instance = get_instance(name=name)
    if sync_instance:
        return get_potenda_from_instance(sync_instance=sync_instance, branch=branch, show_progress=show_progress)
    else:
        return None
