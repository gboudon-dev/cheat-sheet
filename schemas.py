from pydantic import BaseModel, Field, EmailStr

class CommandDTO(BaseModel):
     command_id: int
     language_id: int
     name: str = Field(max_length=100)
     #Temporary string extensions for "description" and "example". The definitive values will be defined after visual interface tests
     description: str = Field(max_length=150)
     example: str = Field(max_length=150)
     is_default: bool
     counter: int = 0

class NoteConfigDTO(BaseModel):
    theme_color: str = "yellow"
    opacity: float = 1.0
    is_always_on_top: bool = True

class NoteDTO(BaseModel):
    note_id: int 
    user_id: int
    pos_x: int 
    pos_y: int 
    note_config: NoteConfigDTO
    commands: list[CommandDTO] = Field(default=list)

class UserDTO(BaseModel):
     user_id: int
     name: str | None = Field(default=None, max_length=50)
     mail: EmailStr | None = Field(default=None, max_length=100)
     password: str | None = Field(default=None, max_length=255)
     notes: list[NoteDTO] = []
  
class LanguageDTO(BaseModel):
    language_id: int
    name: str = Field(max_length=100)
  