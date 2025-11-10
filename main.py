from fastapi import APIRouter, FastAPI
from router import router



app=FastAPI(title = " KEKA Application ")

app.include_router(router)

