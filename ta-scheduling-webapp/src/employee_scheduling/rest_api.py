from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uuid import uuid4
# Custom imports
from .domain import Timetable
from .utils  import DemoData, generate_demo_data, initialize_logger, DataConstructor
from .solver import solver_manager



app = FastAPI(title="TA Shift Rostering",
                description="API for managing ta schedules.",
                docs_url='/q/swagger-ui',
                edoc_url="/redoc-docs",
                debug=True,
                contact={"name": "API Support", "email": "support@example.com"},
                license_info={"name": "Apache 2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0.html"}
            )
data_sets: dict[str, Timetable] = {}

logger = initialize_logger()
logger.info("initialized the 'app' logger")

@app.get("/demo-data")
async def demo_data_list() -> list[str]:
    return [e for e in DemoData]


@app.get("/demo-data/{dataset_id}",  response_model_exclude_none=True)
async def get_demo_data(dataset_id: str) -> Timetable:
    logger.info(f"DEMO-DATA: fetching the problem for {dataset_id} dataset_id")
    demo_data = getattr(DemoData, dataset_id)
    logger.info(f"The demo key is {demo_data}")
    return generate_demo_data(demo_data)

# API call to create timetable from data folder
@app.get("/get/{data_folder}", response_model_exclude_none=True)
async def get_timetable_from_data_folder(data_folder: str) -> Timetable:
    logger.info(f"Extracting data from {data_folder}")
    constructor = DataConstructor(
        ta_csv_path=f"data/{data_folder}/ta_list.csv",
        shift_csv_path=f"data/{data_folder}/shift_list.csv",
        availability_folder=f"data/{data_folder}/availability",
        load= True
    )
    logger.info(f"timetable extracted? {constructor.timetable is not None}")
    return constructor.timetable


@app.get("/schedules/{problem_id}",  response_model_exclude_none=True)
async def get_timetable(problem_id: str) -> Timetable:
    schedule = data_sets[problem_id]
    return schedule.model_copy(update={
        'solver_status': solver_manager.get_solver_status(problem_id)
    })

@app.get("/schedules")
async def list_schedules() -> dict[str, str]:
    return {problem_id: f"{data_sets[problem_id].id}--status: {solver_manager.get_solver_status(problem_id)}" for problem_id in data_sets}


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
