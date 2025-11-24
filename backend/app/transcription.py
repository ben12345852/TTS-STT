import os
import io
import tempfile
import whisper
from mistralai import Mistral

# Whisper Modell laden (beim Start)
print("Lade Whisper Modell...")
whisper_model = whisper.load_model("base")
print("Whisper Modell geladen!")

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
        
        try:
            # Whisper Transkription
            result = whisper_model.transcribe(
                temp_path,
                language="de",  # Deutsch
                fp16=False  # CPU-kompatibel
            )
            
            return {
                'text': result["text"],
                'language': result.get("language", "de")
            }
        finally:
            # Temporäre Datei löschen
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        print(f"Transkriptionsfehler: {e}")
        return {
            'text': None,
            'language': None,
            'error': str(e)
        }


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
