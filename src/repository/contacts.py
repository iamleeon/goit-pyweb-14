"""
Contacts Repository Module

This module provides functions for handling contacts in the database.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate

from datetime import datetime, timedelta, date
from sqlalchemy import and_, func


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    The function returns a list of contacts for a user with pagination param.

    :param skip: A number of contacts to skip.
    :type skip: int
    :param limit: A maximum contacts number to show.
    :type limit: int
    :param user: To get contacts for a specified user.
    :type user: User
    :param db: A database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    The function returns a contact with a provided contact_id for a specified user.

    :param contact_id: A contact_id to return.
    :type contact_id: int
    :param user: To get a contact for a specified user.
    :type user: User
    :param db: A database session.
    :type db: Session
    :return: A contact with a provided contact_id or None if a contact with a provided id doesn't exist.
    :rtype: Contact | None
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
    """
    The function creates a new contact for a provided user.

    :param body: Contact's data.
    :type body: ContactCreate
    :param user: To create a contact for a specified user.
    :type user: User
    :param db: A database session.
    :type db: Session
    :return: A created contact.
    :rtype: Contact
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        additional_info=body.additional_info,
        user_id=user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    The function removes a contact with a provided id for a provided user.

    :param contact_id: A contact_id to remove.
    :type contact_id: int
    :param user: To remove a contact for a specified user.
    :type user: User
    :param db: A database session.
    :type db: Session
    :return: A removed contact or None if a contact with a provided id doesn't exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
    """
    The function updates contact info for a provided user.

    :param contact_id: A contact id to update.
    :type contact_id: int
    :param body: Updated contact's data
    :type body: ContactUpdate
    :param user: To update a contact for a specified user.
    :type user: User
    :param db: A database session.
    :type db: Session
    :return: An updated contact or None if a contact with a provided id doesn't exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_info = body.additional_info
        db.commit()
    return contact


async def search_contacts(
        db: Session,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
        user: User
) -> List[Contact]:
    """
    The function searches for contacts by a provided first name or last name or email.

    :param db: A database session.
    :type db: Session
    :param first_name: Will be used to search among a first name of all the contacts of a specified user.
    :type first_name: str
    :param last_name: Will be used to search among a last name of all the contacts of a specified user.
    :type last_name: str
    :param email: Will be used to search among an email of all the contacts of a specified user.
    :type email: str
    :param user: To search for contacts of a specified user.
    :type user: User
    :return: A list of the contacts with matches.
    :rtype: List[Contact]
    """
    query = db.query(Contact).filter(Contact.user_id == user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f'%{first_name}%'))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f'%{last_name}%'))
    if email:
        query = query.filter(Contact.email.ilike(f'%{email}%'))

    contacts = query.all()
    return contacts


def get_upcoming_birthdays(db: Session, user: User, days: int = 7) -> List[Contact]:
    """
    The function returns contacts with upcoming birthdays within the specified number of days (7) for a provided user.
    :param db: A database session.
    :type db: Session
    :param user: To search for contacts' upcoming birthdays of a specified user.
    :type user: User
    :param days: A number of days to search for upcoming birthdays (default is 7 days).
    :type days: int
    :return: A list of contacts who have birthdays in the upcoming days.
    :rtype: List[Contact]
    """
    today = date.today()
    end_date = today + timedelta(days=days)

    # Extract the month and day from today's date
    today_month = today.month
    today_day = today.day

    # Extract the month and day from the upcoming_date
    upcoming_month = end_date.month
    upcoming_day = end_date.day

    # Query for contacts with birthdays in the next `days` days
    contacts = db.query(Contact).filter(
        Contact.user_id == user.id,
        (func.extract('month', Contact.birthday) == today_month) &
        (func.extract('day', Contact.birthday) >= today_day) |
        (func.extract('month', Contact.birthday) == upcoming_month) &
        (func.extract('day', Contact.birthday) <= upcoming_day)
    ).all()

    return contacts
