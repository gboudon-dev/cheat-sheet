from pydantic import BaseModel, ConfigDict, Field, EmailStr

class ExampleDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    code: str = Field(max_length=150)
    comment: str | None = Field(default=None, max_length=150)

class CommandDTO(BaseModel):
     model_config = ConfigDict(from_attributes=True)
     command_id: int
     language_id: int
     name: str = Field(max_length=100)
     # Temporary max lengths for description and examples; final values will be set after UI testing
     description: str = Field(max_length=150)
     examples: list[ExampleDTO] | None = Field(default=None)
     is_default: bool
     counter: int = 0

class NoteConfigDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    theme: str = "modern"
    is_always_on_top: bool = True

class NoteDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    note_id: int 
    user_id: int
    pos_x: int
    pos_y: int
    width: int
    height: int
    note_config: NoteConfigDTO
    commands: list[CommandDTO] = Field(default_factory=list)

class UserDTO(BaseModel):
     model_config = ConfigDict(from_attributes=True)
     user_id: int
     name: str | None = Field(default=None, max_length=50)
     mail: EmailStr | None = Field(default=None, max_length=100)
     password_hash: str | None = Field(default=None, max_length=255)
     notes: list[NoteDTO] = []
  
class LanguageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    language_id: int
    name: str = Field(max_length=100)

class SeedCommandDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(max_length=100)
    description: str = Field(max_length=150)
    examples: list[ExampleDTO] | None = None
    is_default: bool = False

class SeedLanguageDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str = Field(max_length=100)
    commands: list[SeedCommandDTO]