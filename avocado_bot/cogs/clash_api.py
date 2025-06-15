from __future__ import annotations
import asyncio, logging, os, random
from typing import Any, Dict, Final
import aiohttp
from discord.ext import commands

API_ROOT: Final = "https://api.clashroyale.com/v1"
_JITTER = 0.5; _MAX=3; _BACK=2.0
log = logging.getLogger("clash_api")

class ClashAPI(commands.Cog):
    def __init__(self, bot):  # type: ignore
        self.bot=bot
        self._hdrs={"Authorization":f"Bearer {os.getenv('CR_API_KEY')}"}
        self._lock=asyncio.Semaphore(2)

    async def _get(self, path:str)->Dict[str,Any]:
        url=f"{API_ROOT}{path}"
        async with self._lock:
            await asyncio.sleep(random.random()*_JITTER)
            for i in range(1,_MAX+1):
                try:
                    async with aiohttp.ClientSession() as s:  # no raise_for_status
                        async with s.get(url,headers=self._hdrs,timeout=15) as r:
                            if r.status == 404:            # clan tag wrong OR off-season
                                log.warning("fetch_404", extra={"url": url})
                                return None               # caller will skip insert
                            r.raise_for_status()         # other errors
                            data = await r.json()
                            log.info("fetch_ok",extra={"url":url})
                            return data
                except Exception as e:
                    log.warning("fetch_err",extra={"url":url,"try":i,"err":str(e)})
                    await asyncio.sleep(_BACK*i)
            raise RuntimeError(f"failed {url}")

    async def get_current_river_race(self,tag:str):
        return await self._get(f"/clans/%23{tag.lstrip('#')}/currentriverrace")