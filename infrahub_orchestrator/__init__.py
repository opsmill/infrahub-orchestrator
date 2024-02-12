from dagster import Definitions

from infrahub_orchestrator.job import diff_job, sync_job
from infrahub_orchestrator.ressources import sync_instance
from infrahub_orchestrator.schedule import netbox_sync_job_schedule

defs = Definitions(
    jobs=[
        diff_job,
        sync_job,
    ],
    resources={
        "sync_instance": sync_instance,
    },
    schedules=[netbox_sync_job_schedule],
)
