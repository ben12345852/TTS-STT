"""
Worker-Prozess für KI-Verarbeitung (Transkription & Zusammenfassung)
Verhindert Blockierung der API und stellt sicher, dass nur eine KI-Instanz läuft
"""
import time
from database import db
from transcription import transcribe_audio, generate_summary

def process_note(note_id: int, audio_data: bytes, mime_type: str):
    """Verarbeite eine einzelne Notiz"""
    try:
        print(f"\n{'='*60}")
        print(f"🎙️  Starte Verarbeitung: Notiz {note_id}")
        print(f"{'='*60}")
        
        # 1. Audio transkribieren
        print(f"📝 Transkribiere Audio...")
        result = transcribe_audio(audio_data, mime_type)
        if result.get('error'):
            print(f"❌ Transkriptionsfehler: {result.get('error')}")
            query = "UPDATE notes SET status = 'error' WHERE id = %s"
            db.execute_query(query, (note_id,))
            return False
        
        transcript = result['text']
        print(f"✅ Transkript erstellt ({len(transcript)} Zeichen)")
        
        # 2. Zusammenfassung generieren
        print(f"📋 Generiere Zusammenfassung...")
        summary = generate_summary(transcript)
        
        # 3. Datenbank aktualisieren
        if summary:
            query = """
                UPDATE notes 
                SET transcript = %s, summary = %s, status = 'completed'
                WHERE id = %s
            """
            db.execute_query(query, (transcript, summary, note_id))
            print(f"✅ Zusammenfassung erstellt")
        else:
            query = """
                UPDATE notes 
                SET transcript = %s, status = 'completed'
                WHERE id = %s
            """
            db.execute_query(query, (transcript, note_id))
            print(f"⚠️  Nur Transkript (keine Zusammenfassung)")
        
        print(f"✅ Notiz {note_id} erfolgreich verarbeitet")
        return True
        
    except Exception as e:
        print(f"❌ Fehler bei Verarbeitung von Notiz {note_id}: {e}")
        import traceback
        traceback.print_exc()
        
        query = "UPDATE notes SET status = 'error' WHERE id = %s"
        try:
            db.execute_query(query, (note_id,))
        except Exception as db_error:
            print(f"❌ DB-Update-Fehler: {db_error}")
        return False

def worker_loop():
    """
    Haupt-Worker-Loop: Sucht nach 'processing' Notizen in der DB
    """
    print("\n" + "="*60)
    print("🚀 KI-Worker gestartet")
    print("="*60 + "\n")
    
    # Datenbank verbinden
    db.connect()
    
    try:
        while True:
            # Suche nach Notizen mit Status 'processing'
            query = """
                SELECT id, audio_data, audio_mime_type 
                FROM notes 
                WHERE status = 'processing' or status = 'error'
                ORDER BY created_at ASC 
                LIMIT 1
            """
            result = db.fetch_one(query)
            
            if result:
                note_id = result['id']
                audio_data = result['audio_data']
                mime_type = result.get('audio_mime_type', 'audio/webm')
                
                # Verarbeiten
                process_note(note_id, audio_data, mime_type)
            else:
                # Keine Aufgaben, kurz warten
                time.sleep(2)
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Worker wird beendet...")
    finally:
        db.disconnect()
        print("👋 Worker beendet\n")

if __name__ == "__main__":
    worker_loop()
