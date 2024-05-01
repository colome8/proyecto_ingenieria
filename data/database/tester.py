from schema import engine
from sqlalchemy import inspect

inspector = inspect(engine)
schema = inspector.get_schema_names()

print(schema)
