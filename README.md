# Cheat Sheet Application

A desktop tool designed to remain visible in a corner of the screen while the user codes. It is aimed at programming students or developers learning a new language, framework, or technology, serving as a quick reference for commands without the need to switch windows.

Upon launching, the app does not present an empty search bar; instead, it displays one or more floating sticky notes containing the most frequently used commands for a specific technology. These notes correspond to the language or technology selected during the user's last session. Each entry displays the command alongside a concise explanation (e.g., `append` — adds an element to the end of a list).

Notes are the core element of the application. They support continuous scrolling to reveal all available commands. Users can fully customize them: adding new commands, removing unused ones, or mixing commands from different languages. The goal is for users to adapt these lists based on the commands they have not yet memorized, providing an immediate reminder without having to look up documentation or consult an AI.

In addition to the notes, the application includes a search engine. This allows users to find commands outside the active note and append them. It does not require exact matches: users can type descriptions in natural language—for instance, "delete dictionary"—to get relevant command suggestions. Once found, any command can be seamlessly added to the active note.

All data is stored locally to ensure the application is fast and fully functional offline. Optionally, data can be synchronized across multiple devices and updated to incorporate new languages or recent software versions.

The ultimate goal is to keep an editable, relevant, and concise list of commands permanently visible on the screen, backed by a search engine to expand or modify it as needed.

---

## 1. System Requirements Specification

### Functional Requirements (FR)
* **FR-01 Multi-language Library Management:** The system must be scalable to support N number of technologies through configuration files or database entries.
* **FR-02 Floating Interface (Sticky Mode):** The window must feature an "Always On Top" property, be resizable by the user, and include horizontal visual guide lines.
* **FR-03 Predictive Search:** A search engine capable of providing real-time suggestions based on the command library and descriptions.
* **FR-04 Active List Builder:** An interface to select commands from the search results and send them directly to the sticky note board.
* **FR-05 Logical Sorting:** Automated alphabetical ordering (A-Z) of the commands present within the active list.
* **FR-06 Local Persistence:** Storage of the session state so that the active list and interface configurations persist when the application is closed.
* **FR-07 Telemetry and Library Improvement:** The system must track the usage frequency of each command via a local counter and send this data anonymously to the cloud to identify the most relevant commands and optimize starter packs in future updates.
* **FR-08 Data Export and Import:** Manual backup capability of the command database into standard formats (JSON/CSV).
* **FR-09 Quick Editing:** Ability to briefly modify descriptions or tags directly from the sticky note interface.
* **FR-10 Element Removal:** The user must be able to remove commands from the active list via an action icon located next to the description.
* **FR-11 Authentication and Cloud Sync:**
  * User Login/Registration module.
  * Automatic synchronization of custom libraries, pinned commands, and interface settings to the cloud.
  * Multi-platform data recovery upon user login.
* **FR-12 Predefined Command Loading:** When activating a new technology, the system must automatically load a "Starter Pack" containing its most common and widely used commands.

### Non-Functional Requirements (NFR)
* **NFR-01 Portability:** Lightweight executable targeting desktop operating systems (Windows/Linux/macOS).
* **NFR-02 Resource Efficiency:** CPU consumption under 1% while in an idle state.
* **NFR-03 Usability:** A minimalist user interface that requires no more than 2 clicks for any primary action.

---

## 2. Architecture and Modeling

### Class Diagram
```mermaid
classDiagram
    %% ─── DOMAIN ───
    User "1" *-- "*" Note : manages lifecycle of
    Note "1" *-- "1" NoteConfig : appearance
    Note "1" o-- "*" Command : contains
    Command "*" --> "1" Language : belongs to

    %% ─── SESSION ───
    SessionManager "1" --> "1" User : owns session of
    SessionManager "1" --> "1" CloudSyncManager : delegates sync
    SessionManager "1" --> "1" DbManager : delegates persistence

    %% ─── UI ───
    MainWindow "1" --> "1" SessionManager : uses
    MainWindow ..> Command : searches and assigns

    %% ─── INFRA ───
    CloudSyncManager "1" ..> "1" AppConfig
    CloudSyncManager "1" ..> "1" DbManager
    DbManager "1" --> "1" AppConfig : queries local version
    DbManager ..> Language : queries
    DbManager ..> Note : persists individual notes

    class MainWindow {
        -SessionManager session_manager
        -list active_note_widgets
        +__init__()
        +init_ui() void
        +refresh_ui() void
        +on_new_note_clicked() void
        +on_note_requested_search(target_note: Note, lang_id: int, keyword: str) void
    }

    class SessionManager {
        -User current_user
        -CloudSyncManager cloud_sync
        -DbManager db_manager
        -int DEFAULT_LOCAL_USER_ID$
        +on_login_clicked(mail: str, password: str) void
        +on_logout_clicked() void
        +on_change_password_clicked(old: str, new: str) void
        +search_commands(lang_id: int, keyword: str) list~Command~
    }

    class DbManager {
        -str db_path
        -sqlite3.Connection connection
        +get_user_notes(user_id: int) list~Note~
        +save_user_notes(notes: list~Note~) bool
        +insert_note(note: Note) int
        +save_note_state(note: Note) bool
        +delete_note(note_id: int) bool
        +get_default_commands(lang_id: int) list~Command~
        +get_commands(lang_id: int, keyword: str) list~Command~
        +sync_commands(data: dict) bool
        +update_command_counter(command_id: int, counter: int) void
        +update_schema(to_version: str) bool
    }

    class User {
        -int user_id
        -str name
        -str mail
        -list~Note~ notes
        +load_user(data: dict) void
        +is_active() bool
        +add_note() Note
        +remove_note(note: Note) void
        +logout() void
    }

    class Note {
        -int note_id
        -int user_id
        -NoteConfig appearance
        -int pos_x
        -int pos_y
        -list~Command~ commands
        +Note(user_id: int)
        +load_default_pack(language_id: int) void
        +update_position(new_x: int, new_y: int) void
        +add_command(cmd: Command) void
        +remove_command(cmd: Command) void
        +sort_items() void
        +to_json() dict
    }

    class CloudSyncManager {
        -str api_endpoint
        -str auth_token
        +authenticate_user(mail: str, password: str) bool
        +download_profile(mail: str) dict
        +upload_profile(data: dict) bool
        +get_remote_hash(mail: str) str
        +change_password(mail: str, old: str, new: str) bool
        +send_counter_info(stats: list) dict
    }

    class AppConfig {
        -int config_id
        -int actual_data_version
        -int actual_app_version
        -str last_sync_hash
        +get_current_versions() dict
        +is_update_available(remote_data: dict) bool
        +set_data_version(version: int) bool
        +compare_hash_status(local_hash: str) int
        +update_sync_hash(new_hash: str) void
    }

    class NoteConfig {
        -str theme_color
        -float opacity
        -bool is_always_on_top
        +update_config(**kwargs) bool
        +reset_defaults() void
        +to_json() dict
    }

    class Language {
        -int language_id
        -str name
    }

    class Command {
        -int command_id
        -int language_id
        -str name
        -str description
        -str example
        -bool is_default
        -int counter
    }
```

### Entity-Relationship Diagram (ERD)
```mermaid
erDiagram
    USERS {
        int user_id PK
        string name "not null"
        string mail "nullable, unique"
        string password_hash "nullable"
    }

    NOTES {
        int note_id PK
        int user_id FK "not null"
        int pos_x "not null"
        int pos_y "not null"
        text note_config "not null (JSON_STRING)"
    }

    NOTE_COMMANDS {
        int note_id PK,FK "not null"
        int command_id PK,FK "not null"
    }

    COMMANDS {
        int command_id PK
        int language_id FK "not null"
        string name "not null"
        text description "not null"
        text example "nullable"
        boolean is_default "not null"
        int counter "not null, default 0"
    }

    LANGUAGES {
        int language_id PK
        string name "not null, unique"
    }

    USERS ||--o{ NOTES : "has"
    NOTES ||--o{ NOTE_COMMANDS : "contains"
    COMMANDS ||--o{ NOTE_COMMANDS : "exists"    
    LANGUAGES ||--o{ COMMANDS : "classifies"
```

---

## 3. Sequence Diagrams

### New Note Creation
```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Win as Presentation (MainWindow)
    participant SM as Session (SessionManager)
    participant ModelUser as Domain (User)
    participant ModelNote as Domain (Note)
    participant Repo as Infrastructure (DbManager)
    participant DB as Database (SQLite File)

    User ->> Win : Click "+" button
    Win ->> SM : on_new_note_clicked()
    SM ->> ModelUser : add_note()
    ModelUser ->> ModelNote : Note(user_id)
    Note over ModelNote : note.note_id = None
    ModelNote -->> ModelUser : note
    ModelUser -->> SM : note
    SM ->> Repo : insert_note(note)
    Repo ->> DB : INSERT INTO NOTES
    DB -->> Repo : last_insert_rowid (note_id)
    Note over Repo : note.note_id = note_id
    Repo -->> SM : note (note_id asignado)
    SM ->> ModelUser : add_note_to_list(note)
    SM -->> Win : note
    Win ->> Win : render_new_note_widget(note)
    Win -->> User : Show new blank active note on screen
```

### Command Search by Keyword
```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Win as Presentation (MainWindow)
    participant SM as Session (SessionManager)
    participant Repo as Infrastructure (DbManager)
    participant DB as Database (SQLite File)

    User ->> Win : Type keyword in searchbar
    Win ->> SM : search_commands(lang_id, keyword)
    SM ->> Repo : get_commands(lang_id, keyword)
    Repo ->> DB : SELECT FROM COMMANDS WHERE ...
    DB -->> Repo : Raw data
    Repo -->> SM : list[Command]
    SM -->> Win : list[Command]
    Win ->> Win : render_searchbar_list(commands)
    Win -->> User : Show filtered command list
```

### Loading Default Command Packs
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Win as Presentation (MainWindow)
    participant SM as Session (SessionManager)
    participant ModelNote as Domain (Note)
    participant Repo as Infrastructure (DbManager)
    participant DB as Database (SQLite File)

    User ->> Win : Selects New Language
    Win ->> SM : on_new_language(note: Note, lang_id: int)
    SM ->> Repo : get_default_commands(lang_id: int)
    Repo ->> DB : SELECT FROM COMMANDS WHERE is_default AND lang_id
    DB -->> Repo : Raw data
    Repo -->> SM : list[Command]
    SM ->> ModelNote : load_default_pack(language_id: int, commands : list[Command])
    Win ->> Win : render commands note
    Win -->> User : Show updated note on screen
```

