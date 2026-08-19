from __future__ import annotations
from sqlalchemy import String, ForeignKey, Table, Column, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
      pass

note_command_association = Table(
     "note_commands",
     Base.metadata,
     Column("note_id", ForeignKey("notes.note_id", ondelete="CASCADE"), primary_key=True),
     Column("command_id", ForeignKey("commands.command_id", ondelete="CASCADE"), primary_key=True)
)

class UserORM(Base):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    mail: Mapped[str | None] = mapped_column(String(100), unique=True)
    password_hash: Mapped[str| None] = mapped_column(String(255))
    notes: Mapped[list[NoteORM]] = relationship(back_populates="user")

class NoteORM(Base):
     __tablename__ = "notes"
     note_id: Mapped[int] = mapped_column(primary_key=True)
     user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
     pos_x: Mapped[int]
     pos_y: Mapped[int]
     width: Mapped[int]
     height: Mapped[int]
     note_config: Mapped[dict] = mapped_column(JSON)
     user: Mapped[UserORM] = relationship(back_populates="notes")
     commands: Mapped[list[CommandORM]] = relationship(
          secondary=note_command_association,
          back_populates="notes"
     )

class CommandORM(Base):
     __tablename__ = "commands"
     command_id: Mapped[int] = mapped_column(primary_key=True)
     language_id: Mapped[int] = mapped_column(ForeignKey("languages.language_id"))
     language: Mapped[LanguageORM] = relationship(back_populates="commands")
     notes: Mapped[list[NoteORM]] = relationship(
          secondary=note_command_association,
          back_populates="commands")
     name: Mapped[str] = mapped_column(String(100))
     #Temporary string extensions for "description" and "example". The definitive values will be defined after visual interface tests
     description: Mapped[str] = mapped_column(String(150))
     example: Mapped[str | None] = mapped_column(String(150))
     is_default: Mapped[bool] 
     counter: Mapped[int] = mapped_column(default=0)
    
class LanguageORM(Base):
     __tablename__ = "languages"
     language_id: Mapped[int] = mapped_column(primary_key=True)
     name: Mapped[str] = mapped_column(String(100), unique=True)
     commands: Mapped[list[CommandORM]] = relationship(back_populates="language")