from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import Optional
from database import db
from datetime import datetime
import asyncio
import functools

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
               audio_duration, audio_mime_type, summary, status
        FROM notes 
        ORDER BY created_at DESC
    """
    notes = db.fetch_all(query)
    
    # Audio-URL für Notizen mit Audio hinzufügen
    for note in notes:
        if note.get('audio_mime_type'):
            note['has_audio'] = True
            note['audio_url'] = f"/api/notes/{note['id']}/audio"
        else:
            note['has_audio'] = False
    
    print(notes)
    return {"notes": notes}

@app.get("/api/notes/{note_id}")
def get_note(note_id: int):
    """Eine Notiz abrufen"""
    query = """
        SELECT id, title, created_at, updated_at, 
               audio_duration, audio_mime_type, transcript, manual_notes, summary, status
        FROM notes 
        WHERE id = %s
    """
    note = db.fetch_one(query, (note_id,))
    if not note:
        return {"error": "Notiz nicht gefunden"}, 404
    
    # Audio-URL hinzufügen, falls Audio vorhanden
    if note.get('audio_mime_type'):
        note['audio_url'] = f"/api/notes/{note_id}/audio"
    
    return note

@app.get("/api/notes/{note_id}/audio")
def get_note_audio(note_id: int):
    """Audio-Daten einer Notiz abrufen"""
    query = """
        SELECT audio_data, audio_mime_type
        FROM notes 
        WHERE id = %s AND audio_data IS NOT NULL
    """
    result = db.fetch_one(query, (note_id,))
    
    if not result or not result.get('audio_data'):
        return {"error": "Keine Audio-Daten gefunden"}, 404
    
    # Audio als Response zurückgeben
    return Response(
        content=result['audio_data'],
        media_type=result.get('audio_mime_type', 'audio/webm')
    )

@app.post("/api/notes")
async def create_note(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    text_content: Optional[str] = Form(None),
    audio_duration: Optional[int] = Form(0),
    audio_file: Optional[UploadFile] = File(None)
):
    """Neue Notiz erstellen mit Audio und/oder Text"""
    
    # Audio-Datei verarbeiten, falls vorhanden
    if audio_file:
        # Audio-Datei als Binärdaten lesen
        audio_data = await audio_file.read()
        audio_mime_type = audio_file.content_type
        
        # Audio direkt in Datenbank als BLOB speichern
        # Manuelle Notizen in manual_notes speichern
        query = """
            INSERT INTO notes (title, manual_notes, audio_data, audio_mime_type, audio_duration, status)
            VALUES (%s, %s, %s, %s, %s, 'processing')
        """
        note_id = db.execute_query(query, (title, text_content or "", audio_data, audio_mime_type, audio_duration))
        
        # Transkription im Hintergrund ausführen
        background_tasks.add_task(process_transcription, note_id, audio_data, audio_mime_type)
        
    else:
        # Nur Text-Notiz - in manual_notes speichern
        query = """
            INSERT INTO notes (title, manual_notes, audio_duration, status)
            VALUES (%s, %s, %s, 'completed')
        """
        note_id = db.execute_query(query, (title, text_content or "", 0))
    
    # Erstellte Notiz zurückgeben
    return {
        "id": note_id,
        "title": title,
        "manual_notes": text_content,
        "audio_duration": audio_duration,
        "status": "processing" if audio_file else "completed"
    }


def process_transcription(note_id: int, audio_data: bytes, mime_type: str):
    """
    Hintergrund-Task für Transkription und Zusammenfassung
    Läuft in separatem Thread zur Vermeidung von Memory-Konflikten
    """
    # Import hier, um Threading-Probleme zu vermeiden
    from transcription import transcribe_audio, generate_summary
    
    try:
        # 1. Audio transkribieren
        print(f"Starte Transkription für Notiz {note_id}...")
        result = transcribe_audio(audio_data, mime_type)
        
        if result.get('error') or not result.get('text'):
            # Fehler bei Transkription
            query = "UPDATE notes SET status = 'error' WHERE id = %s"
            db.execute_query(query, (note_id,))
            print(f"Transkriptionsfehler für Notiz {note_id}: {result.get('error')}")
            return
        
        transcript = result['text']
        
        # 2. Zusammenfassung generieren
        print(f"Generiere Zusammenfassung für Notiz {note_id}...")
        summary = generate_summary(transcript)
        
        # 3. Datenbank aktualisieren
        if summary:
            query = """
                UPDATE notes 
                SET transcript = %s, summary = %s, status = 'completed'
                WHERE id = %s
            """
            db.execute_query(query, (transcript, summary, note_id))
        else:
            # Nur Transkript, keine Zusammenfassung
            query = """
                UPDATE notes 
                SET transcript = %s, status = 'completed'
                WHERE id = %s
            """
            db.execute_query(query, (transcript, note_id))
        
        print(f"Transkription für Notiz {note_id} abgeschlossen")
        
    except Exception as e:
        print(f"Fehler bei Verarbeitung von Notiz {note_id}: {e}")
        import traceback
        traceback.print_exc()
        query = "UPDATE notes SET status = 'error' WHERE id = %s"
        try:
            db.execute_query(query, (note_id,))
        except Exception as db_error:
            print(f"DB-Update-Fehler: {db_error}")
