import uuid
from pathlib import Path
from timeit import default_timer as timer

from dagster import (
    AssetKey,
    AssetMaterialization,
    Failure,
    Field,
    In,
    MetadataValue,
    Nothing,
    Out,
    Output,
    get_dagster_logger,
    op,
)
from infrahub_sdk import InfrahubClientSync
from infrahub_sync.utils import render_adapter


@op(out={"source_id": Out(str), "destination_id": Out(str)})
def initialize_adapters_op():
    logger = get_dagster_logger()

    source_id = str(uuid.uuid4())[:8]
    destination_id = str(uuid.uuid4())[:8]

    logger.info(f"Source Store ID  {source_id}")
    logger.info(f"Destination Store ID {destination_id}")

    return source_id, destination_id


@op(
    required_resource_keys={"potenda_resource"},
    ins={"id": In(str)},
    out={"result": Out(str)},
)
def load_sync_source_op(context, id):
    logger = get_dagster_logger()

    if not context.resources.potenda_resource:
        logger.error("Potenda resource is None. Unable to proceed with loading the source.")
        raise Failure("Potenda resource is None. Check the resource configuration.")

    # logger.info(f"Loading the Source {context.resources.potenda_resource.source.name}")
    # start_time = timer()

    # logger.debug(f"Source Store ID {context.resources.potenda_resource.source.store._store_id}")
    # # context.resources.potenda_resource.source.store._store_id = id
    # context.resources.potenda_resource.source_load()
    # end_time = timer()

    # yield AssetMaterialization(
    #         asset_key=f"load-{context.resources.potenda_resource.source.name}",
    #         metadata={
    #             "Load Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
    #             "Store ID": MetadataValue.text(context.resources.potenda_resource.source.store.__str__()),
    #             "Store Item Count": MetadataValue.int(context.resources.potenda_resource.source.store.count()),
    #         },
    #     )
    yield Output(f"{context.resources.potenda_resource.source.store._store_id}", "result")



@op(
    required_resource_keys={"potenda_resource"},
    ins={"id": In(str)},
    out={"result": Out(str)},
)
def load_sync_destination_op(context, id):
    logger = get_dagster_logger()

    if not context.resources.potenda_resource:
        logger.error("Potenda resource is None. Unable to proceed with loading the destination.")
        raise Failure("Potenda resource is None. Check the resource configuration.")

    # logger.info(f"Loading the Destination {context.resources.potenda_resource.destination.name}")
    # start_time = timer()

    # logger.debug(f"Destination Store ID {context.resources.potenda_resource.destination.store._store_id}")
    # # context.resources.potenda_resource.destination_load.store._store_id = id
    # context.resources.potenda_resource.destination_load()
    # end_time = timer()

    # yield AssetMaterialization(
    #         asset_key=f"load-{context.resources.potenda_resource.destination.name}",
    #         metadata={
    #             "Load Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
    #             "Store ID": MetadataValue.text(context.resources.potenda_resource.destination.store.__str__()),
    #             "Store Item Count": MetadataValue.int(context.resources.potenda_resource.destination.store.count()),
    #         },
    #     )
    yield Output(f"{context.resources.potenda_resource.destination.store._store_id}", "result")


@op(
    ins={
        "load_sync_source": In(str),
        "load_sync_destination": In(str),
    },
    out={"result": Out(is_required=False)},
    required_resource_keys={"potenda_resource"},
)
def diff_op(context, load_sync_source, load_sync_destination):
    logger = get_dagster_logger()

    if not context.resources.potenda_resource:
        logger.error("Potenda resource is None. Unable to proceed with diff.")
        raise Failure("Potenda resource is None. Check the resource configuration.")
    logger.info(f"Starting Diff from {context.resources.potenda_resource.source.name} to {context.resources.potenda_resource.destination.name}")

    # Load Source
    logger.info(f"Loading the Source {context.resources.potenda_resource.source.name}")
    start_time = timer()
    logger.debug(f"Source Store ID {context.resources.potenda_resource.source.store._store_id}")
    context.resources.potenda_resource.source_load()
    end_time = timer()

    yield AssetMaterialization(
            asset_key=f"load-{context.resources.potenda_resource.source.name}",
            metadata={
                "Load Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Store ID": MetadataValue.text(context.resources.potenda_resource.source.store.__str__()),
                "Store Item Count": MetadataValue.int(context.resources.potenda_resource.source.store.count()),
            },
        )
    # Load Destination
    logger.info(f"Loading the Destination {context.resources.potenda_resource.destination.name}")
    start_time = timer()
    logger.debug(f"Destination Store ID {context.resources.potenda_resource.destination.store._store_id}")
    context.resources.potenda_resource.destination_load()
    end_time = timer()

    yield AssetMaterialization(
            asset_key=f"load-{context.resources.potenda_resource.destination.name}",
            metadata={
                "Load Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Store ID": MetadataValue.text(context.resources.potenda_resource.destination.store.__str__()),
                "Store Item Count": MetadataValue.int(context.resources.potenda_resource.destination.store.count()),
            },
        )

    # Diff
    potenda_name = f"{context.resources.potenda_resource.source.name}-{context.resources.potenda_resource.destination.name}"
    start_time = timer()
    mydiff = context.resources.potenda_resource.diff()
    end_time = timer()
    diff_full = mydiff.str()
    context.log_event(
        AssetMaterialization(
            asset_key=f"diff-{potenda_name}",
            description="Diff between source and destination Adapters",
            metadata={
                "Diff Exec Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Full Diff": MetadataValue.text(diff_full),
            },
        )
    )
    logger.info(f"Ending Diff from {context.resources.potenda_resource.source.name} to {context.resources.potenda_resource.destination.name}")
    yield Output(f"{end_time - start_time}", "result")

@op(
    config_schema={
        "diff": Field(bool, default_value=False, is_required=False),
    },
    ins={
        "load_sync_source": In(str),
        "load_sync_destination": In(str),
    },
    out={"result": Out(is_required=False)},
    required_resource_keys={"potenda_resource"},
)
def sync_op(context, load_sync_source, load_sync_destination):
    logger = get_dagster_logger()

    if not context.resources.potenda_resource:
        logger.error("Potenda resource is None. Unable to proceed with sync.")
        raise Failure("Potenda resource is None. Check the resource configuration.")
    diff = context.op_config.get("diff", False)
    # FIXME
    # Store ID doesn't seem to be maintain across Operations
    # Doing both load() into the sync_op for now

    # Load Source
    logger.info(f"Loading the Source {context.resources.potenda_resource.source.name}")
    start_time = timer()
    logger.debug(f"Source Store ID {context.resources.potenda_resource.source.store._store_id}")
    context.resources.potenda_resource.source_load()
    end_time = timer()

    yield AssetMaterialization(
            asset_key=f"load-{context.resources.potenda_resource.source.name}",
            metadata={
                "Load Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Store ID": MetadataValue.text(context.resources.potenda_resource.source.store.__str__()),
                "Store Item Count": MetadataValue.int(context.resources.potenda_resource.source.store.count()),
            },
        )
    # Load Destination
    logger.info(f"Loading the Destination {context.resources.potenda_resource.destination.name}")
    start_time = timer()
    logger.debug(f"Destination Store ID {context.resources.potenda_resource.destination.store._store_id}")
    context.resources.potenda_resource.destination_load()
    end_time = timer()

    yield AssetMaterialization(
            asset_key=f"load-{context.resources.potenda_resource.destination.name}",
            metadata={
                "Load Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Store ID": MetadataValue.text(context.resources.potenda_resource.destination.store.__str__()),
                "Store Item Count": MetadataValue.int(context.resources.potenda_resource.destination.store.count()),
            },
        )

    # Diff
    potenda_name = f"{context.resources.potenda_resource.source.name}-{context.resources.potenda_resource.destination.name}"
    start_time = timer()
    mydiff = context.resources.potenda_resource.diff()
    end_time = timer()
    diff_full = mydiff.str()

    if diff:
        diff_full = mydiff.str()
    else:
        diff_full = None
    yield AssetMaterialization(
        asset_key=f"diff-{potenda_name}",
        metadata={
            "Diff Exec Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
            "Full Diff": MetadataValue.text(diff_full),
        },
    )
    # Sync
    if mydiff.has_diffs():
        start_time = timer()
        mydiff = context.resources.potenda_resource.sync(diff=mydiff)
        diff_summary = mydiff.summary()
        end_time = timer()
        yield AssetMaterialization(
            asset_key="sync",
            metadata={
                "Sync Exec Time (sec)": MetadataValue.float(float(f"{end_time - start_time}")),
                "Nbr of objects Created": MetadataValue.int(diff_summary["create"]),
                "Nbr of objects Updated": MetadataValue.int(diff_summary["update"]),
                "Nbr of objects Deleted": MetadataValue.int(diff_summary["delete"]),
                "Nbr of objects Unchanged": MetadataValue.int(diff_summary["no-change"]),
                "Related asset": MetadataValue.asset(AssetKey(f"diff-{potenda_name}")),
            },
        )
        logger.info(f"Ending Sync from {context.resources.potenda_resource.source.name} to {context.resources.potenda_resource.destination.name}")
        yield Output(f"{end_time - start_time}", "result")

@op(
    ins={"rendered_files": In(list)},
    out={"completion_signal": Out(Nothing)},
)
def load_and_materialize_file_op(context, rendered_files: list):
    logger = get_dagster_logger()
    for file_infos in rendered_files:
        template_name, file_path = file_infos
        try:
            with open(file_path, "r") as file:
                file_content = file.read()
                logger.info(f"File {template_name} at {file_path} loaded successfully.")

                adapter = Path(file_path).parts[-2]
                file = Path(file_path).stem
                yield AssetMaterialization(
                    asset_key=f"{adapter}-{file}",
                    description=f"Rendered {template_name}",
                    metadata={
                        "File path": MetadataValue.path(file_path),
                        "File content": MetadataValue.text(file_content),
                        "Adapter": MetadataValue.text(adapter.title()),
                    }
                )
        except IOError as e:
            logger.error(f"Failed to load file {template_name} from {file_path}: {e}")

    yield Output(None, "completion_signal")


@op(
        required_resource_keys={"sync_instance_resource"},
        out={"rendered_files": Out(is_required=False)},
)
def render_adapter_files_op(context):
    sync_instance = context.resources.sync_instance_resource

    if not sync_instance.source or not sync_instance.destination:
        raise Failure("Sync Instance resource does not contain a source and a destination")

    if sync_instance.source.name == "infrahub":
        address = sync_instance.source.settings["url"]
    elif sync_instance.destination.name == "infrahub":
        address = sync_instance.destination.settings["url"]
    else:
        raise Failure("Unable to determine Infrahub Address.")

    client = InfrahubClientSync(address=address)
    schema = client.schema.all()
    rendered_files = render_adapter(sync_instance=sync_instance, schema=schema)

    yield Output(rendered_files, "rendered_files")
