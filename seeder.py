import json
from pathlib import Path
from sqlalchemy.orm import Session
from domain import User
from models import LanguageORM, CommandORM, UserORM
from schemas import SeedLanguageDTO

class DataSeeder:
    LOCAL_USER_NAME: str = "Guest"

    def __init__(self, json_path: Path):
        self._json_path = json_path

    def seed_local_user(self, session: Session) -> None:
        local_user = session.query(UserORM).filter_by(user_id=User.LOCAL_USER_ID).first()
        if local_user:
            return

        local_user = UserORM(
            user_id = User.LOCAL_USER_ID,
            name = self.LOCAL_USER_NAME,
        )
        session.add(local_user)
        session.commit()

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
                    examples_as_dict = None
                    if cmd_dto.examples is not None:
                        examples_as_dict = []
                        for example_dto in cmd_dto.examples:
                            examples_as_dict.append(example_dto.model_dump())

                    cmd_orm = CommandORM(
                        name = cmd_dto.name,
                        description = cmd_dto.description,
                        examples = examples_as_dict,
                        is_default = cmd_dto.is_default
                    )
                    commands_as_orm.append(cmd_orm)

                lang_orm = LanguageORM(
                    name = lang_dto.name,
                    commands = commands_as_orm
                )

                session.add(lang_orm)
            session.commit()


