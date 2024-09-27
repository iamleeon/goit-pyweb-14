from typing import List, Optional

from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactCreate, ContactUpdate

from datetime import datetime, timedelta, date
from sqlalchemy import and_, func


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactCreate, user: User, db: Session) -> Contact:
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
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, user: User, db: Session) -> Contact | None:
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
