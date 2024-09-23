from fastapi import APIRouter

from fastapi import APIRouter

from src.releases.exceptions import ReleaseNotFoundError
from src.utils.dependency import ReleasesServiceDep
from src.utils.exceptions import exception_handler

router = APIRouter(prefix='/releases', tags=['Releases'])


@router.get('')
@exception_handler
async def get_chats(
        service: ReleasesServiceDep,
):
    releases = await service.get_all()

    return {
        'data': releases,
        'detail': 'Releases were selected.'
    }


@router.get('/latest')
@exception_handler
async def get_latest(
        system: str,
        service: ReleasesServiceDep,
):
    release = await service.get_latest(system)
    if not release:
        raise ReleaseNotFoundError

    return {
        'data': release,
        'detail': 'Release were selected.'
    }
