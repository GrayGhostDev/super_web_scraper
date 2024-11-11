```python
import pytest
from database.connection import DatabaseConnection
from database.models import Profile, Company
from sqlalchemy.future import select
from datetime import datetime

@pytest.mark.integration
class TestDatabaseIntegration:
    @pytest.fixture(autouse=True)
    def setup(self, db_connection):
        self.db = db_connection
        self.session = next(self.db.get_session())

    async def test_profile_creation(self):
        """Test creating and retrieving a profile."""
        profile = Profile(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            title="Software Engineer",
            company="Test Company",
            created_at=datetime.utcnow()
        )

        self.session.add(profile)
        await self.session.commit()

        # Retrieve the profile
        stmt = select(Profile).where(Profile.email == "john.doe@example.com")
        result = await self.session.execute(stmt)
        saved_profile = result.scalar_one()

        assert saved_profile is not None
        assert saved_profile.first_name == "John"
        assert saved_profile.last_name == "Doe"

    async def test_company_profile_relationship(self):
        """Test relationship between company and profiles."""
        company = Company(
            name="Test Company",
            domain="testcompany.com",
            industry="Technology"
        )

        profile = Profile(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@testcompany.com",
            company_info=company
        )

        self.session.add(company)
        self.session.add(profile)
        await self.session.commit()

        # Retrieve company with profiles
        stmt = select(Company).where(Company.domain == "testcompany.com")
        result = await self.session.execute(stmt)
        saved_company = result.scalar_one()

        assert saved_company is not None
        assert len(saved_company.profiles) == 1
        assert saved_company.profiles[0].email == "jane.smith@testcompany.com"

    async def test_profile_update(self):
        """Test updating profile information."""
        # Create profile
        profile = Profile(
            first_name="Alice",
            last_name="Johnson",
            email="alice.j@example.com"
        )

        self.session.add(profile)
        await self.session.commit()

        # Update profile
        profile.title = "Senior Engineer"
        profile.company = "New Company"
        await self.session.commit()

        # Verify update
        stmt = select(Profile).where(Profile.email == "alice.j@example.com")
        result = await self.session.execute(stmt)
        updated_profile = result.scalar_one()

        assert updated_profile.title == "Senior Engineer"
        assert updated_profile.company == "New Company"
```