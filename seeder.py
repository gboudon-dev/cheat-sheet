import json
from sqlalchemy.orm import Session
from models import LanguageORM, CommandORM
from schemas import SeedCommandDTO, SeedLanguageDTO

class DataSeeder:
    def __init__(self, json_path: str = "initial_data.json"):
        self._json_path = json_path

    def seed_initial_languages(self, session: Session) -> None:
        if session.query(LanguageORM).count() > 0:
            return

        with open(self._json_path, "r", encoding="utf-8") as json_file:
            raw_data = json.load(json_file)

        languages_list = raw_data.get("languages", [])

        if languages_list:
            for language in languages_list:
                lang_dto = SeedLanguageDTO.model_validate(language)
            
                commands_as_orm = []
                for cmd_dto in lang_dto.commands:
                    cmd_orm = CommandORM(
                        name = cmd_dto.name,
                        description = cmd_dto.description,
                        examples = cmd_dto.examples,
                        is_default = cmd_dto.is_default
                    )
                    commands_as_orm.append(cmd_orm)

                lang_orm = LanguageORM(
                    name = lang_dto.name,
                    commands = commands_as_orm
                )

                session.add(lang_orm)
            session.commit()


