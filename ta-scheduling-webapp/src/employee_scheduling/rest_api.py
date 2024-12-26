from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
# Custom imports
from .domain import Timetable
from .utils  import DemoData, generate_demo_data, initialize_logger
from .solver import solver_manager


app = FastAPI(docs_url='/q/swagger-ui', )
data_sets: dict[str, Timetable] = {}

logger = initialize_logger()
logger.info("initialized the 'app' logger")

# Demo data API
@app.get("/demo-data")
async def demo_data_list() -> list[str]:
    return [e for e in DemoData]


@app.get("/demo-data/{dataset_id}",  response_model_exclude_none=True)
async def get_demo_data(dataset_id: str) -> Timetable:
    logger.info(f"DEMO-DATA: fetching the problem for {dataset_id} dataset_id")
    demo_data = getattr(DemoData, dataset_id)
    logger.info(f"The demo key is {demo_data}")
    return generate_demo_data(demo_data)

# END OF DEMO DATA

@app.get("/schedules/{problem_id}",  response_model_exclude_none=True)
async def get_timetable(problem_id: str) -> Timetable:
    schedule = data_sets[problem_id]
    return schedule.model_copy(update={
        'solver_status': solver_manager.get_solver_status(problem_id)
    })


def update_schedule(problem_id: str, schedule: Timetable):
    global data_sets
    data_sets[problem_id] = schedule


@app.post("/schedules")
async def solve_timetable(schedule: Timetable) -> str:
    job_id = str(uuid4())
    data_sets[job_id] = schedule
    solver_manager.solve_and_listen(job_id, schedule,
                                    lambda solution: update_schedule(job_id, solution))
    return job_id


@app.delete("/schedules/{problem_id}")
async def stop_solving(problem_id: str) -> None:
    solver_manager.terminate_early(problem_id)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
