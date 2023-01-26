from prefect.deployments import Deployment
from prefect.orion.schemas.schedules import CronSchedule
from ride_duration_score import ride_durartion_prediction


deployment = Deployment.build_from_flow(
    flow=ride_durartion_prediction,
    name='ride_duration_prediction',
    schedule=CronSchedule(cron="0 3 2 * *")
    parameters={
        "taxi_type":"green",
        "run_id":"e041808c2a2849919731587f28600398"

    },
    tags=["ml"],

)

deployment.apply()