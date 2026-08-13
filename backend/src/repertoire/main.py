from fastapi import FastAPI

from repertoire.api import (
    health,
    pieces,
    practice_goal,
    practice_sessions,
    repertoire_lists,
    sheet_resources,
)

app = FastAPI(title="Repertoire")

app.include_router(health.router, prefix="/api")
app.include_router(pieces.router, prefix="/api")
app.include_router(practice_sessions.router, prefix="/api")
app.include_router(practice_goal.router, prefix="/api")
app.include_router(sheet_resources.router, prefix="/api")
app.include_router(repertoire_lists.router, prefix="/api")
