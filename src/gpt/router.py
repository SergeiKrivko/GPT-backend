from typing import Annotated

from fastapi import APIRouter, Query, Path

from loguru import logger

from src.gpt import gpt

from src.utils.exceptions import exception_handler, NotFoundError
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
    name: Annotated[str, Path(description="GPT model name", example="default")],
    message: Annotated[str, Query(description="Message to ask GPT")] = "Hello!",
):
    if name not in gpt.get_models():
        raise NotFoundError("Model not found.")

    logger.info(f"Trying {name} with message: {message}.")
    answer = await gpt.async_simple_response(message=message, model=name)
    logger.info(f"Answer: {answer}.")

    return {
        "data": answer,
        "detail": "GPT answer was created.",
    }
