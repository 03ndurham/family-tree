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


    def add_family_member(self, name, date_of_birth, date_of_death=None, sex=None, notes=None, photo=None):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        cursor.execute("""
                       INSERT INTO FamilyMembers (name, date_of_birth, date_of_death, sex, notes, photo) VALUES (?,?,?,?,?)""", 
                       (name, date_of_birth, date_of_death, sex, notes, photo))
        self.conn.commit()
        return cursor.lastrowid


    def add_relationship(self, child_id: int, parent_id: int):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        
        # Check if the relationship already exists
        cursor.execute("""SELECT 1 FROM Relationships WHERE child_id = ? AND parent_id = ?""", (child_id, parent_id))
        if cursor.fetchone():
            print (f'Relationship already exists: child {child_id} -> parent {parent_id}')
            return
        
        cursor.execute("""
                       INSERT INTO Relationships (child_id, parent_id)
                       VALUES (?,?)
                       """, (child_id, parent_id))
        self.conn.commit()
        print(f'Relationship added: child {child_id} -> parent {parent_id}')
        
        
    def search_members_by_name(self, name_fragment):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM FamilyMembers
            WHERE name LIKE ?
        """, (f"%{name_fragment}%",))
        
        return cursor.fetchall()
    
    
    def get_all_members(self):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM FamilyMembers")
        return cursor.fetchall()


    def get_member_by_id(self, member_id):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM FamilyMembers WHERE id = ?", (member_id,))
        return cursor.fetchone()
    
    def get_parents(self, child_id):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT fm.* FROM FamilyMembers fm
            JOIN Relationships r ON r.parent_id = fm.id
            WHERE r.child_id = ?
        """, (child_id,))
        return cursor.fetchall()
    
    
    def get_children(self, parent_id):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        cursor.execute("""
                       SELECT fm.* FROM FamilyMembers fm
                       JOIN Relationships r ON r.child_id = fm.id
                       WHERE r.parent_id =?
                       """, (parent_id,))
        return cursor.fetchall()


    def add_person(self, name, dob, dod=None, sex=None, notes=None, photo=None, parent_ids = None):
        member_id = self.add_family_member(name, dob, dod, sex, notes, photo)
        
        if parent_ids:
            for pid in parent_ids:
                self.add_relationship(parent_id=pid, child_id=member_id)
        
        return member_id
        

    def edit_person(self, member_id, name=None, date_of_birth=None, date_of_death=None,
                       sex=None, notes=None, photo=None, parent_ids=None):
        if not self.conn:
            raise ValueError("Database not loaded.")
        
        cursor = self.conn.cursor()
        
        # Update FamilyMembers fields if provided
        updates = []
        params = []
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if date_of_birth is not None:
            updates.append("date_of_birth = ?")
            params.append(date_of_birth)
        if date_of_death is not None:
            updates.append("date_of_death = ?")
            params.append(date_of_death)
        if sex is not None:
            updates.append("sex = ?")
            params.append(sex)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)
        if photo is not None:
            updates.append("photo = ?")
            params.append(photo)
        
        if updates:
            sql = f"UPDATE FamilyMembers SET {', '.join(updates)} WHERE id = ?"
            params.append(member_id)
            cursor.execute(sql, tuple(params))
        
        # Update Relationships
        if parent_ids is not None:
            # Remove existing parent links
            cursor.execute("DELETE FROM Relationships WHERE child_id = ?", (member_id,))
            # Add new parent links
            for pid in parent_ids:
                if pid is not None:
                    cursor.execute("INSERT INTO Relationships (child_id, parent_id) VALUES (?, ?)", (member_id, pid))
        
        self.conn.commit()
        
    
    def delete_person(self, member_id):
        if not self.conn:
            raise ValueError ("Database not loaded.")
        
        cursor = self.conn.cursor()
        
        cursor.execute("DELETE FROM FamilyMembers Where id = ?", (member_id,))
        print (f'Member {member_id} deleted from FamilyMembers Table.')
        
        cursor.execute("DELETE FROM Relationships WHERE child_id = ? OR parent_id = ?", (member_id, member_id))
        print (f'Member {member_id} deleted from Relationships Table.')
        
        self.conn.commit()