import uvicorn

from employee_scheduling.rest_api import app # Used by Uvicorn for serving the FastAPI app


def main():
    print("-- Running main from __init__.py --")
    config = uvicorn.Config("employee_scheduling:app",
                            port=8080,
                            log_config="logging.conf",
                            use_colors=True)
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    print("inside main")
    main()
