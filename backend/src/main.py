from fastapi import FastAPI
from src.routes import etl_config_router, dashboard_router
from src.middleware.middleware import add_middlewares
from src.routes.api_schemas_route import router as api_schemas_router
from src.models import relationships

app = FastAPI()
add_middlewares(app)


app.include_router(etl_config_router, prefix="/etl/pipeline", tags=["ETL Pipelines"])
app.include_router(api_schemas_router, prefix="/etl/pipeline", tags=["ETL Schemas"])
app.include_router(dashboard_router, prefix="/etl", tags=["ETL Dashboard"])

@app.get("/")
def read_root():
    return {"Hello": "ETL BACKEND"}
