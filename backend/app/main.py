from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db

app = FastAPI(title="Sprach-Notizen API")

# CORS für Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    """Beim Start: Datenbank verbinden"""
    db.connect()

@app.on_event("shutdown")
async def shutdown():
    """Beim Beenden: Datenbank trennen"""
    db.disconnect()

@app.get("/")
def root():
    return {"msg": "Backend OK", "status": "connected"}

@app.get("/api/notes")
def get_notes():
    """Alle Notizen abrufen"""
    query = """
        SELECT id, title, created_at, updated_at, 
               audio_path, audio_duration, summary, status
        FROM notes 
        ORDER BY created_at DESC
    """
    notes = db.fetch_all(query)
    return {"notes": notes}

@app.get("/api/notes/{note_id}")
def get_note(note_id: int):
    """Eine Notiz abrufen"""
    query = """
        SELECT id, title, created_at, updated_at, 
               audio_path, audio_duration, transcript, summary, status
        FROM notes 
        WHERE id = %s
    """
    note = db.fetch_one(query, (note_id,))
    if not note:
        return {"error": "Notiz nicht gefunden"}, 404
    return note
