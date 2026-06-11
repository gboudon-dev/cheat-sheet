from sqlalchemy import String, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
      pass

note_command_association = Table(
     "note_commands",
     Base.metadata,
     Column("note_id", ForeignKey("notes.note_id"), primary_key=True),
     Column("command_id", ForeignKey("commands.command_id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    mail: Mapped[str | None] = mapped_column(String(100), unique=True)
    password: Mapped[str| None] = mapped_column(String(255))
    notes: Mapped[list["Note"]] = relationship(back_populates="user")

class Note(Base):
     __tablename__ = "notes"
     note_id: Mapped[int] = mapped_column(primary_key=True)
     user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
     pos_x: Mapped[int] 
     pos_y: Mapped[int] 
     note_config: Mapped[str] 
     user: Mapped["User"] = relationship(back_populates="notes")
     commands: Mapped[list["Command"]] = relationship(
          secondary=note_command_association,
          back_populates="notes"
     )

class Command(Base):
     __tablename__ = "commands"
     command_id: Mapped[int] = mapped_column(primary_key=True)
     language_id: Mapped[int] = mapped_column(ForeignKey("languages.language_id"))
     language: Mapped["Language"] = relationship(back_populates="commands")
     notes: Mapped[list["Note"]] = relationship(
          secondary=note_command_association,
          back_populates="commands")
     name: Mapped[str] = mapped_column(String(100))
     #Temporary string extensions for "description" and "example". The definitive values will be defined after visual interface tests
     description: Mapped[str] = mapped_column(String(150))
     example: Mapped[str] = mapped_column(String(150))
     is_default: Mapped[bool] 
     counter: Mapped[int] = mapped_column(default=0)
    
class Language(Base):
     __tablename__ = "languages"
     language_id: Mapped[int] = mapped_column(primary_key=True)
     name: Mapped[str] = mapped_column(String(100), unique=True)
     commands: Mapped[list["Command"]] = relationship(back_populates="language")