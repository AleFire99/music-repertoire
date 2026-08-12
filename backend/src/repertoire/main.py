from fastapi import FastAPI

from repertoire.api import health, pieces, practice_sessions

app = FastAPI(title="Repertoire")

app.include_router(health.router, prefix="/api")
app.include_router(pieces.router, prefix="/api")
app.include_router(practice_sessions.router, prefix="/api")
