"""
Fresh Database Initialization
Creates all tables from scratch
"""

from app.core.database import Base, engine
from app.models.organization import OrganizationInfo, MembershipType, OrgStructure
from app.models.member import Member
from app.models.universal_document import UniversalDocument, DocumentCollection

print("🔄 Creating fresh database...")
print("-" * 70)

# Drop all tables (fresh start)
print("\n🗑️  Dropping all existing tables...")
Base.metadata.drop_all(bind=engine)
print("✅ All tables dropped")

# Create all tables
print("\n📦 Creating all tables...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created")

# List created tables
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("\n📊 Database tables created:")
for table in tables:
    print(f"  ✅ {table}")

print("\n" + "=" * 70)
print("✅ Fresh database initialized successfully!")
print("\nDatabase file: kintari.db")
print("Ready to accept data!")
print("=" * 70)
