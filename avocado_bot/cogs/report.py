from __future__ import annotations
import datetime as dt, tempfile, sqlite3
from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt
from zoneinfo import ZoneInfo

PST=ZoneInfo("America/Los_Angeles")
async def generate_report_png(db:Path,snap:bool)->Path:
    today=dt.datetime.now(tz=PST).date().isoformat()
    q="SELECT * FROM current_war WHERE war_date=?" if snap else "SELECT * FROM current_war"
    con = sqlite3.connect(db)
    try:
        df = pd.read_sql_query(q, con, params=(today,) if snap else None)
    finally:
        con.close()

    # empty → caller will send "no data yet"
    if df.empty:
        return None

    def color(r):
        if r.decks_used==4: return "#045d15" if r.score>=3000 else "#154f23"
        if 1<=r.decks_used<=3: return "#665b00"
        return "#5d0b0b"
    fig,ax=plt.subplots(figsize=(10,max(4,len(df)*0.35))); ax.axis("off")
    t=ax.table(cellText=df[["name","decks_used","score","fame","donations"]].values,
               colLabels=["Player","Decks","Score","Fame","Donations"],
               loc="center",cellLoc="center")
    for i,c in enumerate(df.apply(color,axis=1).tolist(),start=1):
        for j in range(5): t[(i,j)].set_facecolor(c)
    fig.tight_layout()
    out=Path(tempfile.gettempdir())/f"war_{dt.datetime.now().timestamp():.0f}.png"
    fig.savefig(out,dpi=150,bbox_inches="tight"); plt.close(fig); return out