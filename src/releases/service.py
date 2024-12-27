import asyncio
import os
from typing import Iterable

from github import Github, Auth
from github.GitRelease import GitRelease

from src.releases.schemas import ReleaseRead, ReleaseAssetRead


class ReleasesService:
    def __init__(self):
        # auth = Auth.Token(os.getenv('GITHUB_TOKEN'))

        # Public Web GitHub
        self.__github = Github()
        self.__repo = self.__github.get_repo('SergeiKrivko/GPT-chat-cs')

    async def get_all(self) -> Iterable[ReleaseRead]:
        res: Iterable[GitRelease] = await asyncio.to_thread(lambda: self.__repo.get_releases())
        return [self.__git_release_to_read_model(r) for r in res]

    async def get_latest(self, system: str) -> ReleaseAssetRead | None:
        releases = await self.get_all()
        for release in releases:
            for asset in release.assets:
                if asset.system == system:
                    return asset
        return None

    @staticmethod
    def __git_release_to_read_model(release: GitRelease) -> ReleaseRead:
        version = release.tag_name.lstrip('v')
        assets = []
        for asset in release.assets:
            if asset.name.count('_') < 2:
                continue
            match asset.name.split('.')[-1]:
                case 'exe':
                    system = 'win'
                case 'deb':
                    system = 'linux'
                case 'dmg':
                    system = 'mac'
                case _:
                    continue
            match asset.name.split('.')[-2].split('_')[-1]:
                case 'amd64':
                    system += '-x64'
                case 'arm64':
                    system += '-arm64'
                case _:
                    continue
            assets.append(ReleaseAssetRead(version=version, system=system, url=asset.browser_download_url))
        return ReleaseRead(version=version, description=release.body, assets=assets)
