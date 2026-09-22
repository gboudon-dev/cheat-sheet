# Cheat Sheet Application

A desktop tool designed to remain visible in a corner of the screen while the user codes. It is aimed at programming students or developers learning a new language, framework, or technology, serving as a quick reference for commands without the need to switch windows.

Upon launching, the app does not present an empty search bar; instead, it displays one or more floating sticky notes containing the most frequently used commands for a specific technology. These are the notes left open in the previous session, each one restored with its own language, commands, position, and size. Each entry displays the command alongside a concise explanation (e.g., `append` — adds an element to the end of a list).

Notes are the core element of the application. They support continuous scrolling to reveal all available commands. Users can fully customize them: adding new commands or removing unused ones. Each note belongs to a single language; to work with two languages, the user opens two notes. The goal is for users to adapt these lists based on the commands they have not yet memorized, providing an immediate reminder without having to look up documentation or consult an AI.

In addition to the notes, the application includes a search engine. This allows users to find more commands of the note's language and append them. It does not require exact matches: typing part of a command name shows real-time suggestions. Once found, any command can be seamlessly added to the active note.

All data is stored locally to ensure the application is fast and fully functional offline.

The ultimate goal is to keep an editable, relevant, and concise list of commands permanently visible on the screen, backed by a search engine to expand or modify it as needed.

---

## 1. System Requirements Specification

### Functional Requirements (FR)
* **FR-01 Multi-language Library Management:** The system must be scalable to support N number of technologies through configuration files or database entries.
* **FR-02 Floating Interface (Sticky Mode):** The window must feature an "Always On Top" property and be resizable by the user.
* **FR-03 Predictive Search:** A search engine capable of providing real-time suggestions by command name within the note's language.
* **FR-04 Active List Builder:** An interface to select commands from the search results and send them directly to the sticky note board.
* **FR-05 Logical Sorting:** Automated alphabetical ordering (A-Z) of the commands present within the active list.
* **FR-06 Local Persistence:** Storage of the session state so that the active list and interface configurations persist when the application is closed.
* **FR-10 Element Removal:** The user must be able to remove commands from the active list via a context menu on each command.
* **FR-12 Predefined Command Loading:** When activating a new technology, the system must automatically load a "Starter Pack" containing its most common and widely used commands.

### Non-Functional Requirements (NFR)
* **NFR-03 Usability:** A minimalist user interface that requires no more than 2 clicks for any primary action.

### Roadmap
Planned features that are not implemented yet:
* **Search by description (FR-03):** Suggestions based on command descriptions as well as names, so users can type what they want to do in natural language (e.g., "delete dictionary").
* **FR-07 Telemetry and Library Improvement:** The system must track the usage frequency of each command via a local counter and send this data anonymously to the cloud to identify the most relevant commands and optimize starter packs in future updates.
* **FR-08 Data Export and Import:** Manual backup capability of the command database into standard formats (JSON/CSV).
* **FR-09 Quick Editing:** Ability to briefly modify descriptions or tags directly from the sticky note interface.
* **FR-11 Authentication and Cloud Sync:**
  * User Login/Registration module.
  * Automatic synchronization of custom libraries, pinned commands, and interface settings to the cloud.
  * Multi-platform data recovery upon user login.
* **NFR-01 Portability:** Lightweight executable targeting desktop operating systems (Windows/Linux/macOS). Currently developed and tested on Windows only.
* **NFR-02 Resource Efficiency:** CPU consumption under 1% while in an idle state.

---

## 2. Architecture and Modeling

### Class Diagram
```mermaid
classDiagram
    %% ─── DOMAIN ───
    User "1" *-- "*" Note : manages lifecycle of
    Note "1" *-- "1" NoteConfig : appearance
    Note "1" o-- "*" Command : contains
    Note "*" --> "0..1" Language : scoped to
    Command "*" --> "1" Language : belongs to

    %% ─── CONTROLLER ───
    AppController "1" --> "1" SessionManager : forwards UI events to

    %% ─── SESSION ───
    SessionManager "1" --> "1" User : owns session of
    SessionManager "1" --> "1" CloudSyncManager : delegates sync
    SessionManager "1" --> "1" DbManager : delegates persistence

    %% ─── INFRA ───
    CloudSyncManager "1" ..> "1" AppConfig
    CloudSyncManager "1" ..> "1" DbManager
    DbManager "1" --> "1" AppConfig : queries local version
    DbManager "1" --> "1" Database : opens sessions through
    DbManager ..> Language : queries
    DbManager ..> Note : persists individual notes
    Bootstrap ..> Database : creates the schema
    Bootstrap ..> DataSeeder : seeds on startup

    class AppController {
        -SessionManager session_manager
        -dict windows
        -callable on_all_windows_closed
        +open_note_window(note: Note) StickyNoteWindow
        +open_saved_notes() list~StickyNoteWindow~
    }

    class SessionManager {
        -User current_user
        -CloudSyncManager cloud_sync
        -DbManager db_manager
        -list~Language~ languages
        +on_login_clicked(mail: str, password: str) void
        +on_logout_clicked() void
        +on_change_password_clicked(old: str, new: str) void
        +get_notes() list~Note~
        +create_note() Note | None
        +remove_note(note_id: int) void
        +close_note(note: Note) void
        +move_note(note: Note, x: int, y: int) void
        +resize_note(note: Note, width: int, height: int) void
        +set_note_always_on_top(note: Note, value: bool) void
        +set_note_language(note: Note, language_id: int) void
        +add_command_to_note(note: Note, command: Command) void
        +remove_command_from_note(note: Note, command: Command) void
        +get_languages() list~Language~
        +search_commands(language_id: int, keyword: str) list~Command~
    }

    class DbManager {
        -sessionmaker session_factory
        -to_domain_command(command_orm: CommandORM) Command
        -note_fields_to_orm(note: Note, note_orm: NoteORM) void
        +get_local_user(user_id: int) User
        +insert_new_note(note: Note) int
        +save_note_state(note: Note) void
        +delete_note(note_id: int) void
        +get_default_commands(language_id: int) list~Command~
        +get_commands(language_id: int, keyword: str) list~Command~
        +get_languages() list~Language~
        +sync_commands(data: dict) bool
        +increment_command_counter(command: Command) void
        +update_schema(to_version: str) bool
    }

    class Database {
        -str database_url
        -Engine engine
        -sessionmaker session_factory
        +create_schema() void
    }

    class Bootstrap {
        +initialize_database(database: Database, seeder: DataSeeder) void
    }

    class DataSeeder {
        +str LOCAL_USER_NAME$
        -str json_path
        +seed_local_user(session: Session) void
        +seed_initial_languages(session: Session) void
    }

    class User {
        +int MAX_NOTES$
        +int LOCAL_USER_ID$
        -int user_id
        -str name
        -str mail
        -list~Note~ notes
        +load_user(data: dict) void
        +is_active() bool
        +can_add_note() bool
        +add_note(note: Note) bool
        +remove_note(note_id: int) void
        +logout() void
    }

    class Note {
        +int MIN_WIDTH$
        +int MIN_HEIGHT$
        -int note_id
        -int user_id
        -int language_id
        -NoteConfig config
        -int pos_x
        -int pos_y
        -int width
        -int height
        -list~Command~ commands
        +change_language(language_id: int, default_commands: list~Command~) void
        +update_position(new_x: int, new_y: int) bool
        +update_size(new_width: int, new_height: int) bool
        +add_command(cmd: Command) bool
        +remove_command(cmd: Command) bool
        +is_empty() bool
        -sort_commands() void
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
        +str DEFAULT_THEME$
        +bool DEFAULT_IS_ALWAYS_ON_TOP$
        -str theme
        -bool is_always_on_top
        +update(**kwargs) bool
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
        -list~dict~ examples
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
        int language_id FK "nullable"
        int pos_x "not null"
        int pos_y "not null"
        int width "not null"
        int height "not null"
        json note_config "not null"
    }

    NOTE_COMMANDS {
        int note_id PK,FK "not null"
        int command_id PK,FK "not null"
    }

    COMMANDS {
        int command_id PK
        int language_id FK,UK "not null, unique together with name"
        string name UK "not null, unique together with language_id"
        text description "not null"
        json examples "nullable, list of {code, comment}"
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
    LANGUAGES |o--o{ NOTES : "scopes"
```

---

## 3. Sequence Diagrams

### New Note Creation
```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Win as UI (StickyNoteWindow)
    participant Ctrl as Controller (AppController)
    participant SM as Session (SessionManager)
    participant ModelUser as Domain (User)
    participant ModelNote as Domain (Note)
    participant Repo as Infrastructure (DbManager)
    participant DB as Database (SQLite File)
    participant NewWin as UI (new StickyNoteWindow)

    User ->> Win : Click "New Note" in the menu
    Win ->> Ctrl : new_note_requested(note)
    Ctrl ->> SM : create_note()
    SM ->> ModelUser : can_add_note()
    ModelUser -->> SM : bool
    alt note limit reached
        SM -->> Ctrl : None
        Ctrl ->> Win : show_message("Note limit", ...)
        Win -->> User : Show note limit message
    else note can be added
        SM ->> ModelNote : Note(user_id)
        Note over ModelNote : note.note_id = None
        ModelNote -->> SM : note
        SM ->> Repo : insert_new_note(note)
        Repo ->> DB : INSERT INTO NOTES
        DB -->> Repo : last_insert_rowid (note_id)
        Repo -->> SM : note_id (int)
        Note over SM : note.note_id = note_id
        SM ->> ModelUser : add_note(note)
        SM -->> Ctrl : note
        Ctrl ->> NewWin : open_note_window(note)
        NewWin -->> User : Show new blank note on screen
        Note over Ctrl, NewWin : language_id is None, so the language dialog opens<br/>(see Loading Default Command Packs)
    end
```

### Command Search and Insertion
```mermaid
sequenceDiagram
    autonumber
    actor User as User
    participant Win as UI (StickyNoteWindow)
    participant Ctrl as Controller (AppController)
    participant SM as Session (SessionManager)
    participant ModelNote as Domain (Note)
    participant Repo as Infrastructure (DbManager)
    participant DB as Database (SQLite File)

    User ->> Win : Type keyword in the search box
    Win ->> Ctrl : command_search_requested(note, keyword)
    Ctrl ->> SM : search_commands(note.language_id, keyword)
    SM ->> Repo : get_commands(language_id, keyword)
    Repo ->> DB : SELECT FROM COMMANDS WHERE language_id AND name LIKE keyword
    DB -->> Repo : Raw data
    Repo -->> SM : list[Command]
    SM -->> Ctrl : list[Command]
    Ctrl ->> Win : show_search_results(commands)
    Win -->> User : Show suggestions

    User ->> Win : Pick a suggestion
    Win ->> Ctrl : add_command_requested(note, command)
    Ctrl ->> SM : add_command_to_note(note, command)
    SM ->> ModelNote : add_command(command)
    ModelNote -->> SM : bool (False if already on the note)
    opt command added
        SM ->> Repo : increment_command_counter(command)
        Repo ->> DB : UPDATE COMMANDS SET counter
        SM ->> Repo : save_note_state(note)
        Repo ->> DB : UPDATE NOTES and NOTE_COMMANDS
    end
    Ctrl ->> Win : refresh_commands()
    Win -->> User : Show updated note on screen
```

### Loading Default Command Packs
```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Win as UI (StickyNoteWindow)
    participant Dialog as UI (LanguageSearchDialog)
    participant Ctrl as Controller (AppController)
    participant SM as Session (SessionManager)
    participant ModelNote as Domain (Note)
    participant Repo as Infrastructure (DbManager)
    participant DB as Database (SQLite File)

    User ->> Win : Click "Select Language" in the menu
    Note over User, Win : Also triggered by clicking the search box of a note<br/>without language, or by creating a new note
    Win ->> Ctrl : language_dialog_requested(note)
    Ctrl ->> SM : get_languages()
    SM -->> Ctrl : list[Language] (cached at startup)
    Ctrl ->> Dialog : LanguageSearchDialog(languages).exec()
    User ->> Dialog : Select a language
    Dialog -->> Ctrl : selected_language_id
    Ctrl ->> SM : set_note_language(note, language_id)
    SM ->> Repo : get_default_commands(language_id)
    Repo ->> DB : SELECT FROM COMMANDS WHERE is_default AND language_id
    DB -->> Repo : Raw data
    Repo -->> SM : list[Command]
    SM ->> ModelNote : change_language(language_id, default_commands)
    SM ->> Repo : save_note_state(note)
    Repo ->> DB : UPDATE NOTES and NOTE_COMMANDS
    Ctrl ->> Win : set_language_header(language_name)
    Ctrl ->> Win : refresh_commands()
    Win -->> User : Show note with the starter pack
```

