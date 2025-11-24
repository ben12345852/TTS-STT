-- Sprach-Notizen App Datenbank Initialisierung
CREATE DATABASE IF NOT EXISTS notes CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE notes;

-- Tabelle: notes
CREATE TABLE IF NOT EXISTS notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    audio_data LONGBLOB,  -- Binärdaten (bis 4GB)
    audio_mime_type VARCHAR(100),
    audio_duration INT DEFAULT 0,
    transcript TEXT,  -- Automatisches Transkript von Audio
    manual_notes TEXT,  -- Manuell eingegebene Notizen
    summary TEXT,
    status ENUM('recording', 'processing', 'completed', 'error') DEFAULT 'completed',
    INDEX idx_created_at (created_at)
);

-- Tabelle: reminders
CREATE TABLE IF NOT EXISTS reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    note_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
    INDEX idx_note_id (note_id)
);

-- Beispiel-Daten
INSERT INTO notes (title, transcript, summary, audio_duration,  status) VALUES
    (
        'Meeting mit Team',
        'Heute haben wir uns getroffen, um den aktuellen Projektstatus zu besprechen. Das Team hat große Fortschritte gemacht. Die neue Funktion für die Spracherkennung ist fast fertig. Maria hat die Benutzeroberfläche optimiert und Thomas hat die Backend-Integration abgeschlossen. Wir haben beschlossen, die Beta-Version nächste Woche zu veröffentlichen. Alle Teammitglieder sollen ihre Aufgaben bis Freitag abschließen. Nächstes Meeting ist am Montag um 10 Uhr. Nicht vergessen: Präsentation vorbereiten für den Kunden.',
        '**Meeting-Zusammenfassung:**\n\n• Projektstatus wurde besprochen\n• Spracherkennungs-Feature ist fast fertig\n• UI-Optimierungen von Maria durchgeführt\n• Backend-Integration von Thomas abgeschlossen\n• Beta-Release für nächste Woche geplant\n• Deadline: Freitag für alle Aufgaben\n• Nächstes Meeting: Montag, 10 Uhr\n• To-Do: Kundenpräsentation vorbereiten',
        327,
        'completed'
    ),
    (
        'Einkaufsliste',
        'Milch, Brot, Eier, Käse nicht vergessen. Außerdem noch Tomaten, Gurken und Paprika für den Salat. Kaffee ist auch alle, also zwei Packungen mitnehmen.',
        'Einkaufsliste: Milch, Brot, Eier, Käse, Tomaten, Gurken, Paprika, 2x Kaffee',
        45,
        'completed'
    ),
    (
        'Projektideen',
        'Neue App-Konzepte für mobile Anwendungen. Erste Idee: Fitness-Tracker mit KI-basiertem Coaching. Zweite Idee: Sprach-basierte Notiz-App mit automatischer Zusammenfassung. Dritte Idee: Smart Home Dashboard mit Sprachsteuerung.',
        'App-Ideen:\n1. Fitness-Tracker mit KI-Coaching\n2. Sprach-Notiz-App mit Auto-Zusammenfassung\n3. Smart Home Dashboard mit Voice Control',
        158,
        'completed'
    );
