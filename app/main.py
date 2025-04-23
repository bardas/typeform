from fastapi import FastAPI
import logging
from app.api.response import router
from app.utils.logging import setup_logging
from starlette.responses import JSONResponse


# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="Typeform RAG Chatbot", version="1.0")
app.include_router(router)


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok"})


@app.on_event("startup")
def on_startup():
    logger.info("App started")


@app.on_event("shutdown")
def on_shutdown():
    logger.info("App stopped")
