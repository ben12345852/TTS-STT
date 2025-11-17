# Sprach-Notiz-App mit automatischer Zusammenfassung  
**Projektbeschreibung (Markdown-Version)**

---

## 📌 1. Projektidee und Zielsetzung

Die **Sprach-Notiz-App** ist eine webbasierte Anwendung, die gesprochene Inhalte automatisch in strukturierte Notizen umwandelt. Die App kombiniert:

- **Speech-to-Text (STT)** → automatische Transkription  
- **KI-Zusammenfassungen** → Kernaussagen extrahieren  
- **Text-to-Speech (TTS)** → Zusammenfassungen vorlesen  
- **Notizverwaltung & Export**  
- **Automatische Terminerkennung und Erinnerungen**

Ziel ist es, Notizen **schneller, bequemer und effizienter** zu erstellen – ohne Tastatur. Besonders nützlich für Meetings, Lernen, Autofahren oder spontane Ideen.

---

## 🎯 2. Zielgruppen & Anwendungsszenarien

### • Schüler:innen & Studierende  
Für Lernnotizen, Zusammenfassungen und Vorlesungsmitschriften.

### • Berufstätige  
Meeting-Notizen, Aufgaben, Protokolle, To-Do-Sammlungen.

### • Kreative & Selbstständige  
Ideen, Kundenbesprechungen, Projektentwürfe.

### • Menschen unterwegs  
Notizen per Sprache erfassen, ohne auf dem Handy tippen zu müssen.

---

## 🎤 3. Feature: Transkription (Tab 1)

Die App nutzt **Speech-to-Text**, um gesprochenen Text automatisch zu erfassen.

### Funktionen:
- Live-Transkription während der Aufnahme  
- Vollständige Rohfassung wird im Tab „Transkription“ angezeigt  
- Möglichkeit zur nachträglichen Bearbeitung  
- Grundlage für KI-Zusammenfassung und Terminerkennung  

### Ziel:
Eine **originalgetreue, editierbare Textversion** der gesprochenen Notiz.

---

## 📝 4. Feature: Zusammenfassung (Tab 2)

Im zweiten Tab erzeugt die App eine **KI-basierte Zusammenfassung** der Transkription.

### Funktionen:
- API-Anbindung an ein KI-Modell (Text-Summarization)  
- Erzeugt strukturierte, verkürzte Notizen  
- Automatische Speicherung in der Datenbank  
- Wechsel zwischen Originaltext & Zusammenfassung möglich  

### Vorteil:
Lange Mitschriften werden auf **präzise Kerninformationen** reduziert.

---

## 📂 5. Notizverwaltung

Alle Notizen werden vollständig im System gespeichert:  
**Audio → Transkription → Zusammenfassung → Aktionen**

### Funktionen der Notizverwaltung:
- Listenansicht aller Notizen  
- Suchfunktion (Titel, Inhalt, Datum)  
- Filter & Sortierung  
- Kategorien/Tags  
- Detailansicht einer Notiz  
- Aktionen: Bearbeiten, Löschen, Exportieren, Erinnerung setzen  

### Ziel:
Ein sauber strukturiertes Archiv, das auch bei vielen Notizen übersichtlich bleibt.

---

## ⏰ 6. Automatische Erinnerungen

Die App erkennt **Termine, Zeiten und Aufgaben** automatisch aus dem Transkript.

### Beispiele für erkannte Ausdrücke:
- „Morgen um 18 Uhr Gym“  
- „Nicht vergessen: Präsentation vorbereiten“  
- „Freitag Meeting mit Lukas“

### Funktionen:
- KI analysiert Transkription auf zeitbezogene Daten  
- Vorschlag für automatische Erinnerung  
- Erinnerung kann:
  - intern gespeichert werden  
  - an Google/Apple/Outlook Kalender weitergegeben werden (Kalenderdatei oder API)

### Ziel:
Aus Notizen **automatisch To-Dos und Termine ableiten**, ohne extra Eingaben.

---

## 📤 7. Exportfunktionen

Die App bietet mehrere Exportformate an:

### **1. PDF**
- Saubere, druckfertige Version  
- Enthält Transkription und Zusammenfassung  

### **2. Word (.docx)**
- Weiterbearbeitung in Word, LibreOffice etc. möglich  

### **3. Markdown (.md)**
- Ideal für Entwickler oder Tools wie Obsidian/Notion  

### **4. E-Mail-Template**
- Automatisch generierte E-Mail aus:
  - Titel  
  - Transkription  
  - Zusammenfassung  

### Ziel:
Inhalte flexibel weiterverwenden und teilen können.

---

## 💻 8. Technische Umsetzung

### 🔧 8.1 Frontend (Vue.js)
- Vue 3 SPA mit Tabs:
  - Tab 1: Transkription
  - Tab 2: Zusammenfassung
  - Bereich: Notizverwaltung  
- Nutzung der Web Speech API:
  - STT (SpeechRecognition)  
  - TTS (SpeechSynthesis)  
- API-Kommunikation via Axios  
- Lokale Validierung & State-Management

---

### 🔌 8.2 Backend (Node.js oder Python)

#### Option A – Node.js (Express)
- REST-API mit den Endpunkten:
  - `POST /api/notes`  
  - `GET /api/notes`  
  - `GET /api/notes/:id`  
  - `PUT /api/notes/:id`  
  - `DELETE /api/notes/:id`  
  - `POST /api/summarize`  
  - `POST /api/reminder-detect`  
  - `GET /api/export/:id?format=pdf|docx|md|email`  

#### Option B – Python (FastAPI)
- Gleiche Endpunkte, anderes Ökosystem.

### Aufgaben des Backends:
- KI-Anbindung (Summarization API)  
- Logik zur Terminerkennung  
- Export-Funktion (PDF, DOCX, MD, E-Mail)  
- Datenbankverwaltung  
- Speicherung von Transkripten & Zusammenfassungen  

---

### 🗄️ 8.3 Datenbank

Beispielstruktur (relational oder NoSQL):

#### Tabelle/Collection: `notes`
| Feld | Beschreibung |
|------|--------------|
| id | eindeutige Notiz-ID |
| title | Titel der Notiz |
| created_at | Erstellungsdatum |
| updated_at | Änderungsdatum |
| audio_path | optionaler Audio-Speicherort |
| transcript | lange Rohfassung |
| summary | erzeugte Zusammenfassung |
| tags | Kategorie/Labels |

#### Tabelle/Collection: `reminders`
| Feld | Beschreibung |
|------|--------------|
| id | eindeutige Erinnerung |
| note_id | Bezug zur Notiz |
| remind_at | Datum/Zeit |
| title | Betreff |
| status | aktiv/abgelaufen |

---

## 🔊 9. TTS-Funktion

Der Nutzer kann sich die Zusammenfassung vom Browser vorlesen lassen:

### Optionen:
- Auswahl der Stimme  
- Geschwindigkeit anpassen  
- Pausen/Satzmelodie automatisch verbessern  

---

## ⭐ 10. Mehrwert & Besonderheit des Projekts

Diese App unterscheidet sich stark von einfachen Diktiergeräten:

- Vollautomatisierter Workflow  
- Kombination aus STT, KI-Summary, TTS  
- Strukturierte Verwaltung statt nur Audio-Files  
- Automatische Erinnerungserkennung  
- Professionelle Exportmöglichkeiten  

Sie ist ein echter **Produktivitäts-Booster** und eignet sich sowohl für persönliche Organisation als auch für den beruflichen Einsatz.

---

## 📁 11. Optional: Erweiterungsideen

- Mehrsprachige STT/TTS  
- Cloud-Synchronisierung zwischen Geräten  
- Benutzerkonten & Login  
- Offline-Modus mit lokalen Transkriptionen  
- API für externe Tools (Notion, Obsidian, Google Docs)

---

## ✔️ Fazit

Die Sprach-Notiz-App ist ein vollwertiges, KI-gestütztes Werkzeug zur:

- Notizerfassung  
- Zusammenfassung  
- Organisation  
- Planung  
- Archivierung  

Sie hilft Menschen, **Zeit zu sparen, produktiver zu sein und nichts Wichtiges zu vergessen**.

---