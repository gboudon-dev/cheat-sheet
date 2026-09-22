from database import Database
from seeder import DataSeeder

def initialize_database(database: Database, seeder: DataSeeder) -> None:
    database.create_schema()
    with database.session_factory() as session:
        seeder.seed_local_user(session=session)
        seeder.seed_initial_languages(session=session)
