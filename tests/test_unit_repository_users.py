import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.usermodel = UserModel(username="testname", email="test@email.com", password="secret_password")

    async def test_get_user_by_email_found(self):
        user = User(id=1, username="testname", email=self.usermodel.email)
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=self.usermodel.email, db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="abc@email.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        self.session.add = MagicMock()
        self.session.commit = MagicMock()
        self.session.refresh = MagicMock()
        result = await create_user(body=self.usermodel, db=self.session)
        self.assertEqual(result.username, self.usermodel.username)
        self.assertEqual(result.email, self.usermodel.email)
        self.assertTrue(hasattr(result, "id"))
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    async def test_update_token(self):
        user = User(id=1, username="testname", email=self.usermodel.email)
        self.session.query().filter().first.return_value = user
        await update_token(user=user, token="new_token", db=self.session)
        self.assertEqual(user.refresh_token, "new_token")
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(id=1, username="testname", email=self.usermodel.email, confirmed=False)
        self.session.query().filter().first.return_value = user
        await confirmed_email(email=self.usermodel.email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        user = User(id=1, username="testname", email=self.usermodel.email, avatar="avatar")
        self.session.query().filter().first.return_value = user
        result = await update_avatar(email=self.usermodel.email, url="new_avatar", db=self.session)
        self.assertEqual(result.avatar, "new_avatar")
        self.session.commit.assert_called_once()
