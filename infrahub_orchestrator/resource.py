from typing import Optional

from dagster import (
    Field,
    Noneable,
    String,
    resource,
)
from infrahub_sync import SyncInstance
from infrahub_sync.utils import get_instance, get_potenda_from_instance
from potenda import Potenda


@resource(
    config_schema={
        "name": Field(Noneable(String), is_required=False, description="Name of the sync instance"),
        "config_file": Field(Noneable(String), is_required=False, description="Path to the sync configuration YAML file"),
        "directory": Field(String, is_required=False, default_value="", description="Directory to search for the sync instance or to use with the config file"),
    },
)
def sync_instance_resource(init_context) -> Optional[SyncInstance]:
    name = init_context.resource_config.get("name")
    config_file = init_context.resource_config.get("config_file")
    directory = init_context.resource_config.get("directory")

    if name and config_file:
        init_context.log.error("Please specify either 'name' or 'config_file', not both.")
        return None

    sync_instance = get_instance(name=name, config_file=config_file, directory=directory)
    if not sync_instance:
        init_context.log.error(f"Sync instance could not be loaded from {'name' if name else 'config_file'}.")
        raise Exception("Sync instance could not be loaded.")

    return sync_instance

@resource(
    config_schema={
        "branch": Field(String, default_value="main", is_required=False),
        "show_progress": Field(bool, default_value=False, is_required=False),
    },
    required_resource_keys={"sync_instance_resource"},
)
def potenda_resource(init_context) -> Optional[Potenda]:
    sync_instance = init_context.resources.sync_instance_resource
    branch = init_context.resource_config["branch"]
    show_progress = init_context.resource_config["show_progress"]

    return get_potenda_from_instance(sync_instance=sync_instance, branch=branch, show_progress=show_progress)