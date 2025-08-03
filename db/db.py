from sqlite3 import Connection

# This file only handles schema of databases. 

def initialize_schema(conn: Connection):
    """
    Initializes all database tables if they do not exist.
    Should be called once per connection
    """
    cursor = conn.cursor()
    
    # Table to hold Family Members
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS FamilyMembers (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       name TEXT NOT NULL,
                       date_of_birth DATE NOT NULL,
                       date_of_death DATE,
                       sex TEXT NOT NULL,
                       notes TEXT,
                       photo TEXT
                   );
                   """)
    
    # Table to show Relationships
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Relationships (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       child_id INTEGER NOT NULL,
                       parent_id INTEGER NOT NULL,
                       UNIQUE (child_id, parent_id),
                       FOREIGN KEY (child_id) REFERENCES FamilyMembers(id),
                       FOREIGN KEY (parent_id) REFERENCES FamilyMembers(id)
                   );
                   """)
    
    # Table to set up Schema Version
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS SchemaVersion(
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       version TEXT NOT NULL,
                       applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       notes TEXT
                   );
                   """)
    
    # Commit Schema change to ensure tables are created
    conn.commit()
    

# Function that allows future updates to easily update the schema table with notes.
def ensure_schema_version(cursor, version_label, notes=""):
    cursor.execute("SELECT 1 FROM SchemaVersion WHERE version = ?", (version_label,))
    if cursor.fetchone():
        print(f"Schema version {version_label} already applied.")
        return
    cursor.execute(
        "INSERT INTO SchemaVersion (version, notes) VALUES (?,?);",
        (version_label, notes)
    )
    print(f"Applied schema version {version_label}.")