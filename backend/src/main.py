from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "ETL"}


@app.get("/valami")
def read_valami():
    return {"Hello": "Valami"}