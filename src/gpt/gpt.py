import asyncio
from typing import Optional

import g4f


def stream_response(messages: list[dict[str:str]], model=None, **kwargs):
    if model is None or model == "default":
        model = g4f.models.default

    try:
        response = g4f.ChatCompletion.create(
            model=model, messages=messages, timeout=120, stream=True, **kwargs
        )
        for el in response:
            yield el
    except g4f.StreamNotSupportedError:
        yield simple_response(messages, model, **kwargs)


def simple_response(messages: list[dict[str:str]], model=None, **kwargs):
    if model is None or model == "default":
        model = g4f.models.default

    response = g4f.ChatCompletion.create(
        model=model, messages=messages, timeout=120, **kwargs
    )
    return response


async def async_stream_response(messages: list[dict[str:str]], model=None, **kwargs):
    res = []
    finished = False

    def func():
        for el in stream_response(messages, model, **kwargs):
            res.append(el)
        nonlocal finished
        finished = True

    task = asyncio.create_task(asyncio.to_thread(func))
    while not finished:
        await asyncio.sleep(0.5)
        if res:
            lst = res
            res = []
            yield "".join(lst)
    if res:
        yield "".join(res)
    await task


def get_models():
    yield "default"
    for el in g4f.models._all_models:
        yield el


async def async_simple_response(message: str, model: str = "default") -> str:
    if model == "default":
        model = None

    return " ".join(
        [
            chunk
            async for chunk in async_stream_response(
                [
                    {
                        "role": "user",
                        "content": message,
                    }
                ],
                model=model,
            )
        ]
    )
