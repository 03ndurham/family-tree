## Database 
### FamilyMember Table

Stores core data for each person in the tree.

| Column Name | Type                                                        | Description                                                                                                                                   |
| ----------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`        | INTEGER PRIMARY KEY                                         | Unique ID for each person                                                                                                                     |
| `name`      | TEXT                                                        | Full name                                                                                                                                     |
| `dob`       | DATE (Can be `NULL`)                                        | Date of birth                                                                                                                                 |
| `dod`       | DATE (optional)                                             | Date of death                                                                                                                                 |
| `sex`       | TEXT                                                        | Sex (e.g., M, F, Other.)                                                                                                                       |
| `notes`     | TEXT (Can be `NULL`)                                        | Any additional notes the user may want to include.                                                                                            |
| `photo`     | TEXT (Just a reference to the file location of the picture) | 2. In case the user wants to upload a photo. This stores only a path to the photo, not the image itself, to reduce database size. |

### Relationships Table

Defines parent-child links by storing references to people in the 'FamilyMember' Table.

| Column Name | Type                | Description                     |
| ----------- | ------------------- | ------------------------------- |
| `id`        | INTEGER PRIMARY KEY | Unique ID for each relationship |
| `child_id`  | INTEGER             | ID of child (foreign key)       |
| `parent_id` | INTEGER             | ID of parent (foreign key)      |

- Each Person can appear multiple times - Once per relationship (e.g. as a child, or as a parent).
- No limit to number of children or parents.
- Queryable in both directions: Parent to Child, or Child to Parent

## Database Setup file 
- db.py - The purpose is to create the database(s) with the appropriate tables.
	- Should include `CREATE TABLE IF NOT EXISTS` logic
## Database Manager 
- Loading Databases 
- Unloading Databases 
- Changing / Switching between Databases 
- Acts as communication manager for any modifications to the loaded database 
- Cache read results for faster performance
- Schema versioning (future-proofing in case structure evolves)

## Family Management Module 
- Contains Functions for adding, editing, and deleting Family members 
- This is the bridge between the GUI and the Database Manager 
- use something like `get_family_member_by_id` to fetch members
- maybe include a search by name for better user experience. `search_member_by_name`
- Maybe run a validation check for unique names or duplicate entries.

| Field         | Input Type                               |
| ------------- | ---------------------------------------- |
| Name          | Text                                     |
| Date of Birth | Date                                     |
| Date of Death | Date (optional)                          |
| Parent(s)     | Multiselect dropdown of existing members |
| Sex           | Dropdown (M/F/Other)                     |
- After submission: 
	 - Insert person into `FamilyMember` 
	  - For each selected parent, insert a `Relationship` linking parent → new person

## Tree Generator 
- Contacts Family Management Module to get all family members 
- Generates a tree that expands vertically upward 
- Y-Axis is going to be time -Inserts Box at date of birth for family members, box contains: Name DOB - DOD -Draws lines to show Relation.
- Use Sex to color box Blue (Male), Pink (Female), and Purple (Other).
- Layout challenges with overlapping birth years—add horizontal offsets or staggered rows.
- Potential libraries to explore: `networkx`, `graphviz`, `plotly`, `matplotlib`.

## Steamlit App 
Handles just GUI 
- Welcome page serves as a welcome screen and explains the app 
- Pages directory with: 
	-  1_Database_Management.py - Interface for user to change databases or create new ones (Interacts with Database Manager). When published (shared online) the database will exist only in memory on the users computer. We need an export and import function so users can build over time.
		- Export family data as `.csv`, `.json`, or `.sqlite` file
	-  2_Family_Members.py - Interface for user to add family members, edit family members, delete family members. When selecting parent(s) , drop down multiselect will show existing members or root. This will interact with Family Management Module. 
	-  3_Family_Tree.py - This Draws the actual tree. Will interact with the Tree Generator Module. We should allow the user to choose vertical or horizontal orientation. This will have the option to Add a Title (Top or Bottom). We may want to experiment with different themes in the future.
		- Export tree as `.jpg`, `.png`, or `.pdf`.

## Schema Versioning

**Purpose:** Ensure consistent and compatible database structure as the app evolves over time. This allows updates to be applied without breaking older versions or losing data.

### Metadata Table

Create a dedicated table to store global values like the database schema version:

``` sql
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Insert initial schema version
INSERT OR REPLACE INTO metadata (key, value) VALUES ('schema_version', '1.0');
```

This avoids cluttering other tables and centralizes configuration.

### Migration Workflow

Before launching the app, check the current database version and apply updates as needed:

``` python
def get_schema_version(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM metadata WHERE key='schema_version'")
    result = cursor.fetchone()
    return result[0] if result else '0.0'

def migrate_to_1_1(conn):
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE FamilyMember ADD COLUMN notes TEXT")
    cursor.execute("UPDATE metadata SET value='1.1' WHERE key='schema_version'")
    conn.commit()
```

Then trigger migration logic in app initialization:

``` python
version = get_schema_version(conn)
if version == '1.0':
    migrate_to_1_1(conn)
```

Repeat this for each future update to keep databases in sync.

### Notes & Best Practices

- Always use **ALTER**, **CREATE**, or custom scripts to update schema.
    
- Perform **backups** before major migrations.
    
- Use **semantic versioning** (e.g. `1.1`, `2.0`) to reflect structural changes.
    
- Consider using a migration framework for complex logic (e.g. Alembic for SQLAlchemy).

## Versioning Breakdown

| Version | Trigger Event                               | Example Update                                           |
| ------- | ------------------------------------------- | -------------------------------------------------------- |
| `1.1`   | **MINOR** – Backward-compatible feature     | Adding a `notes` column or export functionality          |
| `2.0`   | **MAJOR** – Breaking change or big overhaul | Renaming tables, changing how relationships are stored   |
| `1.0.1` | **PATCH** – Fixes or small tweaks           | Fixing a bug in migration logic or adjusting constraints |

### When to Bump Versions

- Use **MINOR updates** for:    
    - New optional fields
    - UI enhancements
    - Added functions that don’t change existing ones
- Use **MAJOR updates** for:
    - Rewriting schema logic
    - Changing relationship structures (e.g. allowing “spouse links”)
    - Removing or renaming columns
- Use **PATCH updates** for:
    - Fixing migration code
    - Updating error handling
    - Tweaking default values

I should start at `1.0` when the schema is first created. When you added optional features like a `notes` field or a metadata table—those are perfect candidates for a bump to `1.1`.

If I were to refactor how relationships are stored (say by making a unified `PersonRelations` table that covers siblings, spouses, etc.)—then that would be a `2.0` update.