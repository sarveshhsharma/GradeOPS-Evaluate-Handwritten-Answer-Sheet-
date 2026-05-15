from database import engine, Base
import models # This imports your models so SQLAlchemy knows about the new columns

print("🗑️ Dropping all existing tables...")
Base.metadata.drop_all(bind=engine)

print("✨ Recreating all tables with the new schema...")
Base.metadata.create_all(bind=engine)

print("✅ Database reset complete! The rubric_similarity column now exists.")