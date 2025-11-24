import os
import io
import tempfile
import torch
import gc
from mistralai import Mistral

# Whisper wird lazy geladen (nur wenn benötigt)
whisper_model = None

def get_whisper_model():
    """Lazy loading des Whisper Modells"""
    global whisper_model
    if whisper_model is None:
        import whisper
        print("Lade Whisper Modell...")
        whisper_model = whisper.load_model("base")
        print("Whisper Modell geladen!")
    return whisper_model

# Mistral Client für Zusammenfassung
mistral_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY", ""))

def transcribe_audio(audio_data: bytes, mime_type: str = "audio/webm") -> dict:
    """
    Transkribiert Audio-Daten mit lokalem Whisper Modell
    
    Args:
        audio_data: Audio-Binärdaten
        mime_type: MIME-Type der Audio-Datei
    
    Returns:
        dict mit 'text' (Transkript) und 'language' (erkannte Sprache)
    """
    temp_path = None
    try:
        # Datei-Extension basierend auf MIME-Type
        extension_map = {
            'audio/webm': 'webm',
            'audio/mp3': 'mp3',
            'audio/mpeg': 'mp3',
            'audio/wav': 'wav',
            'audio/ogg': 'ogg',
            'audio/m4a': 'm4a'
        }
        extension = extension_map.get(mime_type, 'webm')
        
        # Temporäre Datei erstellen (Whisper braucht Dateipfad)
        with tempfile.NamedTemporaryFile(suffix=f'.{extension}', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name
        
        # Whisper Modell laden
        model = get_whisper_model()
        
        # Whisper Transkription mit Memory-Management
        with torch.no_grad():  # Keine Gradienten berechnen (spart Memory)
            result = model.transcribe(
                temp_path,
                language="de",  # Deutsch
                fp16=False,  # CPU-kompatibel
                verbose=False  # Weniger Ausgaben
            )
        
        # Memory aufräumen
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return {
            'text': result["text"],
            'language': result.get("language", "de")
        }
        
    except Exception as e:
        print(f"Transkriptionsfehler: {e}")
        import traceback
        traceback.print_exc()
        return {
            'text': None,
            'language': None,
            'error': str(e)
        }
    finally:
        # Temporäre Datei löschen
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Fehler beim Löschen der Temp-Datei: {e}")


def generate_summary(text: str) -> str:
    """
    Generiert eine Zusammenfassung mit Mistral AI (optional)
    Falls kein API Key vorhanden, wird eine einfache Zusammenfassung zurückgegeben
    
    Args:
        text: Der zu zusammenfassende Text
    
    Returns:
        Zusammenfassung als String
    """
    # Prüfen ob Mistral API Key vorhanden
    if not os.getenv("MISTRAL_API_KEY"):
        # Einfache Zusammenfassung ohne API
        lines = text.split('\n')
        if len(text) > 200:
            return f"**Zusammenfassung:**\n\n{text[:200]}..."
        return f"**Zusammenfassung:**\n\n{text}"
    
    try:
        response = mistral_client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein Assistent, der Notizen zusammenfasst. Erstelle eine prägnante Zusammenfassung in Stichpunkten mit Markdown-Formatierung auf Deutsch."
                },
                {
                    "role": "user",
                    "content": f"Fasse folgende Notiz zusammen:\n\n{text}"
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Zusammenfassungsfehler: {e}")
        # Fallback auf einfache Zusammenfassung
        if len(text) > 200:
            return f"**Zusammenfassung:**\n\n{text[:200]}..."
        return f"**Zusammenfassung:**\n\n{text}"
