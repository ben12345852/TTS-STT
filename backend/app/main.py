from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from database import db
import os
from datetime import datetime

app = FastAPI(title="Sprach-Notizen API")

# CORS für Frontend - MUSS vor den Routes kommen
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Upload-Ordner erstellen
UPLOAD_DIR = "/app/uploads/audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

@app.post("/api/notes")
async def create_note(
    title: str = Form(...),
    text_content: Optional[str] = Form(None),
    audio_duration: Optional[int] = Form(0),
    audio_file: Optional[UploadFile] = File(None)
):
    """Neue Notiz erstellen mit Audio und/oder Text"""
    
    audio_path = None
    audio_mime_type = None
    
    # Audio-Datei speichern, falls vorhanden
    if audio_file:
        # Dateiname generieren
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"note-{timestamp}.webm"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Datei speichern
        with open(file_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        audio_path = f"/uploads/audio/{filename}"
        audio_mime_type = audio_file.content_type
        
        # Audio in Datenbank als BLOB speichern
        query = """
            INSERT INTO notes (title, transcript, audio_data, audio_mime_type, audio_duration, status)
            VALUES (%s, %s, %s, %s, %s, 'processing')
        """
        note_id = db.execute_query(query, (title, text_content or "", content, audio_mime_type, audio_duration))
    else:
        # Nur Text-Notiz
        query = """
            INSERT INTO notes (title, transcript, audio_duration, status)
            VALUES (%s, %s, %s, 'completed')
        """
        note_id = db.execute_query(query, (title, text_content or "", 0))
    
    # Erstellte Notiz zurückgeben
    return {
        "id": note_id,
        "title": title,
        "transcript": text_content,
        "audio_path": audio_path,
        "audio_duration": audio_duration,
        "status": "processing" if audio_file else "completed"
    }
