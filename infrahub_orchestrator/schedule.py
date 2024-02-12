from dagster import (
    RunRequest,
    ScheduleEvaluationContext,
    schedule,
)

from infrahub_orchestrator.job import sync_job


@schedule(job=sync_job, cron_schedule="0 9-16 * * 0-5", execution_timezone="Europe/Paris")
def netbox_sync_job_schedule(context: ScheduleEvaluationContext):
    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")
    return RunRequest(
        run_key=None,
        run_config={
            "ops": {
                "sync_job": {
                    "config": {
                        "name": "from-nexbox",
                        "branch": "main",
                        "show_progress": False,
                    },
                }
            }
        },
        tags={"date": scheduled_date},
    )
