from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    The function returns a user by a provided email.

    :param email: An email to search for a user.
    :type email: str
    :param db: A database session.
    :type db: Session
    :return: A user with the provided email or None if no user is found.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The function creates a new user and assigns a Gravatar image if available.

    :param body: The user's data.
    :type body: UserModel
    :param db: A database session.
    :type db: Session
    :return: A created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The function updates the refresh token for a provided user.

    :param user: The user to update the token for.
    :type user: User
    :param token: A new refresh token or None to remove it.
    :type token: str | None
    :param db: A database session.
    :type db: Session
    :return: None
    :rtype: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The function confirms the email of a user.

    :param email: The email to confirm for a user.
    :type email: str
    :param db: A database session.
    :type db: Session
    :return: None
    :rtype: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The function updates the avatar URL for a user by their email.

    :param email: The email of the user to update the avatar for.
    :type email: str
    :param url: The new avatar URL.
    :type url: str
    :param db: A database session.
    :type db: Session
    :return: The updated user.
    :rtype: User
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user

