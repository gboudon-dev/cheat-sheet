import sys
from PySide6.QtWidgets import QApplication

from db_manager import DbManager
from session_manager import SessionManager
from domain import Command
from ui.sticky_note import StickyNoteWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    db_mgr = DbManager()
    session_mgr = SessionManager(db_manager=db_mgr)

    # TEST BLOQUE
    test_note = session_mgr.create_note()
    test_note.title = "Git Quick Commands"
    git_commands = (
    Command(
        command_id=1,
        language_id=1,
        name="git status",
        is_default=True,
        description="Muestra el estado del árbol de trabajo y del área de preparación",
        counter=0
    ),
    Command(
        command_id=2,
        language_id=1,
        name="git add .",
        is_default=True,
        description="Agrega todos los cambios actuales al área de preparación",
        counter=0
    ),
    Command(
        command_id=3,
        language_id=1,
        name='git commit -m "mensaje"',
        is_default=True,
        description="Guarda los cambios confirmados en el historial local con un mensaje",
        counter=0
    ),
    Command(
        command_id=4,
        language_id=1,
        name="git push origin main",
        is_default=True,
        description="Envía las confirmaciones locales a la rama remota principal",
        counter=0
    ),
    Command(
        command_id=5,
        language_id=1,
        name="git pull",
        is_default=True,
        description="Descarga e incorpora los cambios del repositorio remoto",
        counter=0
    ),
    Command(
        command_id=6,
        language_id=1,
        name="git checkout -b nueva-rama",
        is_default=True,
        description="Crea una nueva rama local y se cambia a ella inmediatamente",
        counter=0
    ),
    Command(
        command_id=7,
        language_id=1,
        name="git log --oneline",
        is_default=True,
        description="Muestra el historial de confirmaciones de forma resumida en una línea",
        counter=0
    ),
    Command(
        command_id=8,
        language_id=1,
        name="git stash",
        is_default=True,
        description="Guarda temporalmente los cambios no confirmados para limpiar el directorio",
        counter=0
    ),
    Command(
        command_id=9,
        language_id=1,
        name="git stash pop",
        is_default=True,
        description="Recupera y aplica los últimos cambios guardados temporalmente",
        counter=0
    ),
    Command(
        command_id=10,
        language_id=1,
        name="git restore .",
        is_default=True,
        description="Descarta todos los cambios locales no guardados en el directorio de trabajo",
        counter=0
    ),
)
    for cmd in git_commands:
        test_note.add_command(cmd)
    # END OF TEST BLOQUE
    window = StickyNoteWindow(note=test_note)
    window.always_on_top_changed.connect(session_mgr.set_note_always_on_top)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()