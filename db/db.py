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
                   CREATE TABLE IF NOT EXISTS FamilyMember (
                       id INTEGER PRIMARY KEY,
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
                       id INTEGER PRIMARY KEY,
                       child_id INTEGER NOT NULL,
                       parent_id INTEGER NOT NULL,
                       FOREIGN KEY (child_id) REFERENCES FamilyMember(id),
                       FOREIGN KEY (parent_id) REFERENCES FamilyMember(id)
                   );
                   """)
    
    # Table to set up Schema Version
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS metadata(
                       id INTEGER PRIMARY KEY,
                       version TEXT NOT NULL
                       applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                       notes TEXT
                   );
                   """)
    

# Function that allows future updates to easily update the schema table with notes.
def check_schema_version(cursor, version_label, notes=""):
    cursor.execute("SELECT 1 FROM metadata WHERE version = ?", (version_label,))
    if cursor.fetchone():
        print(f"Schema version {version_label} already applied.")
        return
    cursor.execute(
        "INSERT INTO metadata (version, notes) VALUE (?,?);",
        (version_label, notes)
    )
    print(f"Applied schema version {version_label}.")