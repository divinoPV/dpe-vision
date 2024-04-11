from typing import List

import polars as pl

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/data")
def get_data() -> List[dict]:
    return pl.read_parquet("./data/cleaned.parquet").to_dicts()
