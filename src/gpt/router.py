from typing import Annotated

from fastapi import APIRouter, Query

from loguru import logger

from src.gpt import gpt

from src.utils.exceptions import exception_handler
from src.utils.ratelimit_by_ip import RatelimitByIpDep

router = APIRouter(prefix="/gpt", tags=["GPT"])


@router.get("/models")
@exception_handler
async def get_models_handler():
    return {"data": gpt.get_models(), "detail": "GPT models were selected."}


@router.post(
    "/models/{name}/try",
    summary="Try GPT model",
    description="Ask any GPT for free with trial mode (access limited)",
)
@exception_handler
async def try_model(
    _: RatelimitByIpDep,
    message: Annotated[str, Query(description="Message to ask GPT")],
):
    logger.info("Trying GPT model...")

    return {
        "data": message,
        "detail": "GPT answer was created.",
    }
