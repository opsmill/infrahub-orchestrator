from dagster import Output, graph, job

from infrahub_orchestrator.operation import (
    diff_op,
    initialize_adapters_op,
    load_and_materialize_file_op,
    load_sync_destination_op,
    load_sync_source_op,
    render_adapter_files_op,
    sync_op,
)
from infrahub_orchestrator.resource import potenda_resource, sync_instance_resource


@job(
        resource_defs={
            "sync_instance_resource": sync_instance_resource,
            "potenda_resource": potenda_resource
        }
    )
def diff_job():
    source_id, destination_id = initialize_adapters_op()
    rendered_files = render_adapter_files_op()
    diff_op(
        load_sync_source=load_sync_source_op(source_id),
        load_sync_destination=load_sync_destination_op(destination_id),
        materialize_file=load_and_materialize_file_op(rendered_files=rendered_files),
    )

@job(
        resource_defs={
            "sync_instance_resource": sync_instance_resource,
            "potenda_resource": potenda_resource
        }
    )
def sync_job():
    source_id, destination_id = initialize_adapters_op()
    rendered_files = render_adapter_files_op()
    sync_op(
        load_sync_source=load_sync_source_op(source_id),
        load_sync_destination=load_sync_destination_op(destination_id),
        materialize_file=load_and_materialize_file_op(rendered_files=rendered_files),
    )

@job(
        resource_defs={
            "sync_instance_resource": sync_instance_resource,
            "potenda_resource": potenda_resource
        }
    )
def generate_job():
    rendered_files = render_adapter_files_op()
    load_and_materialize_file_op(rendered_files=rendered_files)
