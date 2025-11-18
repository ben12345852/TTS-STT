import os
import mysql.connector
from mysql.connector import Error
from typing import Optional

class Database:
    def __init__(self):
        self.connection: Optional[mysql.connector.connection.MySQLConnection] = None
        
    def connect(self):
        """Verbindung zur Datenbank herstellen"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', 'example'),
                database=os.getenv('DB_NAME', 'notes'),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            if self.connection.is_connected():
                print("✓ Erfolgreich mit MySQL Datenbank verbunden")
                return True
        except Error as e:
            print(f"✗ Fehler bei Datenbankverbindung: {e}")
            return False
    
    def disconnect(self):
        """Verbindung trennen"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✓ Datenbankverbindung geschlossen")
    
    def execute_query(self, query: str, params: tuple = None):
        """Query ausführen (INSERT, UPDATE, DELETE)"""
        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"✗ Query-Fehler: {e}")
            return None
        finally:
            cursor.close()
    
    def fetch_all(self, query: str, params: tuple = None):
        """Alle Ergebnisse abrufen"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"✗ Query-Fehler: {e}")
            return []
        finally:
            cursor.close()
    
    def fetch_one(self, query: str, params: tuple = None):
        """Ein Ergebnis abrufen"""
        cursor = self.connection.cursor(dictionary=True)
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchone()
        except Error as e:
            print(f"✗ Query-Fehler: {e}")
            return None
        finally:
            cursor.close()

# Globale Datenbank-Instanz
db = Database()
