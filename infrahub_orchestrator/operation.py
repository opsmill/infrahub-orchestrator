import uuid
from timeit import default_timer as timer

from dagster import (
    AssetKey,
    AssetMaterialization,
    Field,
    In,
    MetadataValue,
    Nothing,
    Out,
    get_dagster_logger,
    op,
)


@op(out={"source_id": Out(str), "destination_id": Out(str)})
def initialize_adapters_op():
    logger = get_dagster_logger()

    source_id = str(uuid.uuid4())[:8]
    destination_id = str(uuid.uuid4())[:8]

    logger.info(f"Source ID  {source_id}")
    logger.info(f"Dest ID {destination_id}")

    return (source_id, destination_id)


@op(required_resource_keys={"sync_instance"}, ins={"id": In(str)})
def load_sync_source_op(context, id):
    context.resources.sync_instance.source.store._store_id = id
    context.resources.sync_instance.source_load()


@op(required_resource_keys={"sync_instance"}, ins={"id": In(str)})
def load_sync_destination_op(context, id):
    context.resources.sync_instance.source.store._store_id = id
    context.resources.sync_instance.destination_load()


@op(
    ins={
        "source_id": In(str),
        "load_sync_source": In(Nothing),
        "destination_id": In(str),
        "load_sync_destination": In(Nothing),
    },
    required_resource_keys={"sync_instance"},
)
def diff_op(context, source_id, destination_id):
    logger = get_dagster_logger()

    sync_instance = context.resources.sync_instance
    logger.info(f"Starting Diff for {sync_instance.name}")
    start_time = timer()
    mydiff = sync_instance.diff()
    end_time = timer()
    diff_full = mydiff.str()
    context.log_event(
        AssetMaterialization(
            asset_key="diff",
            description="Diff between source and destination Adapters",
            metadata={
                "diff_exec_time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Full Diff": MetadataValue.text(diff_full),
            },
        )
    )
    logger.info(f"Ending Diff for {sync_instance.name}")


@op(
    config_schema={
        "diff": Field(bool, default_value=False, is_required=False),
    },
    ins={
        "source_id": In(str),
        "load_sync_source": In(Nothing),
        "destination_id": In(str),
        "load_sync_destination": In(Nothing),
    },
    required_resource_keys={"sync_instance"},
)
def sync_op(context, source_id, destination_id):
    logger = get_dagster_logger()

    sync_instance = context.resources.sync_instance
    diff = context.resource_config.get("diff", False)
    logger.info(f"Starting Sync for {sync_instance.name}")
    start_time = timer()
    mydiff = sync_instance.diff()
    end_time = timer()
    diff_full = mydiff.str()
    if not mydiff.has_diffs():
        return None
    if diff:
        diff_full = mydiff.str()
    else:
        diff_full = None
    yield AssetMaterialization(
        asset_key="diff",
        metadata={
            "diff_exec_time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
            "Full Diff": MetadataValue.text(diff_full),
        },
    )
    start_time = timer()
    mydiff = sync_instance.sync(diff=mydiff)
    diff_summary = mydiff.summary()
    end_time = timer()
    yield AssetMaterialization(
        asset_key="sync",
        metadata={
            "sync_exec_time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
            "Nbr of objects Created": MetadataValue.int(diff_summary["create"]),
            "Nbr of objects Updated": MetadataValue.int(diff_summary["update"]),
            "Nbr of objects Deleted": MetadataValue.int(diff_summary["delete"]),
            "Nbr of objects Unchanged": MetadataValue.int(diff_summary["no-change"]),
            "Related asset": MetadataValue.asset(AssetKey("diff")),
        },
    )
    logger.info(f"Ending Sync for {sync_instance.name}")
