from dagster import Definitions

from infrahub_orchestrator.job import diff_job, generate_job, sync_job
from infrahub_orchestrator.resource import potenda_resource, sync_instance_resource
from infrahub_orchestrator.schedule import netbox_sync_job_schedule

defs = Definitions(
    jobs=[
        diff_job,
        sync_job,
        generate_job,
    ],
    resources={
        "potenda_resource": potenda_resource,
        "sync_instance_resource": sync_instance_resource,
    },
    schedules=[netbox_sync_job_schedule],
)
