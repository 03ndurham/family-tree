import sqlite3
from pathlib import Path
from typing import Optional
from db.db import initialize_schema, ensure_schema_version
import json

is_in_development = True


class DatabaseManager:
    
    self.conn: Optional[sqlite3.Connection] = None
    self.path: Optional[Path] = None
    
    
    def load_database(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = (Path(__file__).parent.parent /"db" / "dev_database.db") if is_in_development else ":memory"
            
        self.path = Path(db_path) if db_path != ":memory" else None
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        initialize_schema(self.conn)
        self._check_and_apply_migrations()
        print(f'Database loaded from {db_path}')        
    
    
    def _check_and_apply_migrations(self):
        cursor = self.conn.cursor()
        
        # Confirm SchemaVersion exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' and name='SchemaVersion';")
        if cursor.fetchone() is None:
            initialize_schema(self.conn)
            
        ensure_schema_version(cursor, "1.0", "Initial schema with FamilyMembers and Relationships")
        self.conn.commit()
   
   
    def unload_database(self):
        """Safely closes the current connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")
        self.conn = None
        self.path = None


    def get_connection(self) -> sqlite3.Connection:
        if not self.conn:
            raise ValueError("No database loaded. Call load_database() first.")
        return self.conn


    def export_database(self, export_path: str):
        if not self.conn:
            raise ValueError("No database loaded.")

        if is_in_development:
            # Full SQLite file backup (copy the entire DB)
            with sqlite3.connect(export_path) as out_conn:
                self.conn.backup(out_conn)
            print(f"Database file backed up to {export_path}")
        else:
            # Export JSON (structured data export)
            self.export_to_json(export_path)  # call your JSON export method


    def import_database(self, import_path: str):
        if is_in_development:
            # Unload and reload entire SQLite database file
            self.unload_database()
            self.load_database(import_path)
            print(f"Database file imported from {import_path}")
        else:
            # Import from JSON file into fresh memory DB or persistent DB
            self.import_from_json(import_path)
            print(f"Database imported from JSON file {import_path}")


    def export_to_json(self, export_path: str):
        """Exports FamilyMembers, Relationships, and SchemaVersion tables to a JSON file."""
        if not self.conn:
            raise ValueError("No database loaded.")
        cursor = self.conn.cursor()

        data = {}
        for table in ['FamilyMembers', 'Relationships', 'SchemaVersion']:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            data[table] = [dict(row) for row in rows]

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        print(f"Database exported as JSON to {export_path}")


    def import_from_json(self, import_path: str):
        """Imports FamilyMembers, Relationships, and SchemaVersion data from a JSON file."""
        self.unload_database()
        self.load_database()  # Load fresh DB (file or memory depending on flag)

        with open(import_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        cursor = self.conn.cursor()

        # Clear existing data before import (optional but usually desired)
        cursor.execute("DELETE FROM Relationships")
        cursor.execute("DELETE FROM FamilyMember")
        cursor.execute("DELETE FROM SchemaVersion")
        self.conn.commit()

        # Insert FamilyMembers rows
        for row in data.get('FamilyMembers', []):
            # Remove 'id' because it's auto-increment primary key, or else use REPLACE
            row.pop('id', None)
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?'] * len(row))
            sql = f"INSERT INTO FamilyMembers ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row.values()))

        # Insert Relationships rows (same logic but keep ids as they link parents/children)
        for row in data.get('Relationships', []):
            # I may need to use REPLACE INTO here
            row.pop('id', None)
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?'] * len(row))
            sql = f"INSERT INTO Relationships ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row.values()))
            
        # Insert SchemaVersion rows
        for row in data.get('SchemaVersion', []):
            row.pop('id', None)
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?']) * len(row)
            sql = f"INSERT INTO SchemaVersion ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row.values()))

        self.conn.commit()
        print(f"Database imported from JSON file {import_path}")

"""
Some Additional Methods I may want. Possibly as part of the DatabaseManager Class, or
as it's own class (Family Manager Class)
 - add_family_member(name, date_of_birth, date_of_death, sex, notes, photo)
 - get_all_members()
 - get_member_by_id(id)
 - search_members_by_name(name_fragment)
 - add_relationship(child_id, parent_id)
 - get_parents(child_id)
 - get_children(parent_id)
"""
