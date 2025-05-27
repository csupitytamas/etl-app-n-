from fastapi import FastAPI
from src.routes import etl_config_route
from src.middleware.middleware import add_middlewares

app = FastAPI()
add_middlewares(app)

# Router regisztrálása
app.include_router(etl_config_route.router, prefix="/etl", tags=["ETL Pipelines"])

@app.get("/")
def read_root():
    return {"Hello": "ETL BACKEND"}
