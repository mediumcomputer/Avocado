"""Shared helpers for the Riddle system."""
from __future__ import annotations
import dataclasses, datetime as dt, json, random, io, sqlite3, logging
from pathlib import Path
import matplotlib.pyplot as plt, pandas as pd, discord
from zoneinfo import ZoneInfo

log = logging.getLogger("riddle")
PST = ZoneInfo("America/Los_Angeles")

# -------------------------------------------------- state
@dataclasses.dataclass
class State:
    chan_id: int
    question: str = ""
    answer: str = ""
    solved: bool = False
    # permanent season points
    points: dict[str, int] = dataclasses.field(default_factory=dict)
    # test-battle pts expire (ts, name -> pts)
    test_pts: dict[str, tuple[int, int]] = dataclasses.field(default_factory=dict)

# -------------------------------------------------- util fns
def next_seconds(h: int, m: int) -> float:
    now = dt.datetime.now(tz=PST)
    tgt = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if tgt <= now: tgt += dt.timedelta(days=1)
    return (tgt - now).total_seconds()

def load_bank() -> list[dict[str,str]]:
    p = Path(__file__).with_name("riddles.json")
    return json.loads(p.read_text()) if p.exists() else []

def random_riddle() -> tuple[str,str]:
    bank = load_bank()
    pick = random.choice(bank) if bank else {"question":"No riddles","answer":"none"}
    return pick["question"], pick["answer"]

# -------------------------------------------------- pretty PNG
def score_png(rows:list[tuple[str,int]])-> io.BytesIO:
    df = pd.DataFrame(rows, columns=["Player","Pts"]).sort_values("Pts",ascending=False)
    fig, ax = plt.subplots(figsize=(4,0.5+0.4*len(df))); ax.axis("off")
    if df.empty:
        ax.text(.5,.5,"No scores yet",ha="center",va="center"); buf=io.BytesIO()
        fig.savefig(buf,format="png",dpi=120,bbox_inches="tight"); buf.seek(0); plt.close(fig); return buf
    tbl=ax.table(cellText=df.values,colLabels=df.columns,cellLoc="center",loc="center")
    for (r,_),c in tbl.get_celld().items():
        if r==0: c.set_facecolor("#2e7d32"); c.get_text().set_color("w")
    plt.tight_layout(); buf=io.BytesIO(); fig.savefig(buf,format="png",dpi=120,bbox_inches="tight")
    buf.seek(0); plt.close(fig); return buf
