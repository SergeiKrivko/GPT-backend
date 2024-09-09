import asyncio

import g4f


def stream_response(messages: list[dict[str: str]], model=None, **kwargs):
    if model is None or model == 'default':
        model = g4f.models.default

    try:
        response = g4f.ChatCompletion.create(
            model=model,
            messages=messages,
            timeout=120,
            stream=True,
            **kwargs
        )
        for el in response:
            yield el
    except g4f.StreamNotSupportedError:
        yield simple_response(messages, model, **kwargs)


# async def async_stream_response(messages: list[dict[str: str]], model=None, **kwargs):
#     if model is None or model == 'default':
#         model = g4f.models.default
#
#     try:
#         response = g4f.ChatCompletion.create_async(
#             model=model,
#             messages=messages,
#             timeout=120,
#             stream=True,
#             **kwargs
#         )
#         async for el in response:
#             yield el
#     except g4f.StreamNotSupportedError:
#         async for el in async_simple_response(messages, model, **kwargs):
#             yield el


def simple_response(messages: list[dict[str: str]], model=None, **kwargs):
    if model is None or model == 'default':
        model = g4f.models.default

    response = g4f.ChatCompletion.create(
        model=model,
        messages=messages,
        timeout=120,
        **kwargs
    )
    return response


# async def async_simple_response(messages: list[dict[str: str]], model=None, **kwargs):
#     if model is None or model == 'default':
#         model = g4f.models.default
#
#     response = g4f.ChatCompletion.create_async(
#         model=model,
#         messages=messages,
#         timeout=120,
#         **kwargs
#     )
#     async for el in response:
#         yield el


async def async_stream_response(messages: list[dict[str: str]], model=None, **kwargs):
    print(3)
    res = []
    finished = False

    model = 'gpt-4o-mini'

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
            yield ''.join(lst)
    if res:
        yield ''.join(res)
    await task


def get_models():
    yield 'default'
    for el in g4f.models._all_models:
        yield el