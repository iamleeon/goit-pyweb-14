import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    search_contacts,
    get_upcoming_birthdays,
)

from datetime import date, timedelta


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactCreate(
            first_name="test",
            last_name="contact",
            email="test@email.com",
            phone="+380501234567",
            birthday="2024-09-28"
        )
        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone, body.phone)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactUpdate(
            first_name="test",
            last_name="contact",
            email="test@email.com",
            phone="+380501234567",
            birthday="2024-09-28",
            additional_info="optional text"
        )
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(
            first_name="test",
            last_name="contact",
            email="test@example.com",
            phone="+380501234567",
            birthday="2024-09-28",
            additional_info="optional text"
        )
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_search_contacts_found(self):
        contact = Contact(id=1, first_name="Taras", last_name="Tarasiuk", email="taras@example.com", phone="+380509876543", birthday="2024-09-28")
        contacts = [contact]
        self.session.query().filter().filter().all.return_value = contacts
        result = await search_contacts(self.session, first_name="John", last_name=None, email=None, user=self.user)
        self.assertEqual(result, contacts)

    async def test_search_contacts_not_found(self):
        self.session.query().filter().filter().all.return_value = []
        result = await search_contacts(self.session, first_name="Abc", last_name=None, email=None, user=self.user)
        self.assertEqual(result, [])

    async def test_get_upcoming_birthdays_found(self):
        today = date.today()
        upcoming_birthday = today + timedelta(days=5)
        contact = Contact(id=1, first_name="Taras", last_name="Tarasiuk", email="taras@example.com", phone="+380509876543", birthday=upcoming_birthday)
        self.session.query().filter().all.return_value = [contact]
        result = get_upcoming_birthdays(db=self.session, user=self.user)
        self.assertEqual(result, [contact])

    async def test_get_upcoming_birthdays_not_found(self):
        self.session.query().filter().all.return_value = []
        result = get_upcoming_birthdays(db=self.session, user=self.user)
        self.assertEqual(result, [])
