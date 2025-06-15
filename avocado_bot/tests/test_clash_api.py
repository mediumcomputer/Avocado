import os, pytest, asyncio
from aioresponses import aioresponses
from cogs.clash_api import ClashAPI, API_ROOT
@pytest.mark.asyncio
async def test_api():
    os.environ["CR_API_KEY"]="x"
    with aioresponses() as m:
        m.get(f"{API_ROOT}/clans/%23TAG/currentriverrace",payload={"clan":{"participants":[]}})
        api=ClashAPI(None)  # type: ignore
        data=await api.get_current_river_race("#TAG")
        assert "clan" in data