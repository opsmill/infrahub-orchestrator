from dagster import job

from infrahub_orchestrator.operation import (
    diff_op,
    initialize_adapters_op,
    load_sync_destination_op,
    load_sync_source_op,
    sync_op,
)
from infrahub_orchestrator.ressources import sync_instance


@job(resource_defs={"sync_instance": sync_instance})
def diff_job():
    source_id, destination_id = initialize_adapters_op()

    diff_op(
        source_id=source_id,
        load_sync_source=load_sync_source_op(source_id),
        destination_id=destination_id,
        load_sync_destination=load_sync_destination_op(destination_id),
    )


@job(resource_defs={"sync_instance": sync_instance})
def sync_job():
    source_id, destination_id = initialize_adapters_op()

    sync_op(
        source_id=source_id,
        load_sync_source=load_sync_source_op(source_id),
        destination_id=destination_id,
        load_sync_destination=load_sync_destination_op(destination_id),
    )
