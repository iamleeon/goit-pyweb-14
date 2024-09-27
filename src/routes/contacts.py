from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import ContactCreate, ContactUpdate, ContactResponse
from src.repository import contacts as repository_contacts

from src.database.models import User
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/",
            response_model=List[ContactResponse],
            description='No more than 12 requests per minute',
            dependencies=[Depends(RateLimiter(times=12, seconds=60))])
async def read_contacts(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function returns a paginated list of contacts for the current user.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of contacts.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts


@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
        first_name: Optional[str] = Query(None, description="First name to search"),
        last_name: Optional[str] = Query(None, description="Last name to search"),
        email: Optional[str] = Query(None, description="Email to search"),
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function searches for contacts by first name, last name, or email for the current user.

    :param first_name: First name to search.
    :type first_name: str | None
    :param last_name: Last name to search.
    :type last_name: str | None
    :param email: Email to search.
    :type email: str | None
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of contacts matching the search criteria.
    :rtype: List[ContactResponse]
    """
    contacts = await repository_contacts.search_contacts(db, first_name, last_name, email,  current_user)
    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(default=7),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function returns contacts with upcoming birthdays within the specified number of days.

    :param days: Number of days to look ahead for upcoming birthdays (default is 7 days).
    :type days: int
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: A list of contacts with upcoming birthdays.
    :rtype: List[ContactResponse]
    """
    contacts = repository_contacts.get_upcoming_birthdays(db,  current_user, days)
    return contacts


@router.get("/{contact_id}",
            response_model=ContactResponse,
            description='No more than 12 requests per minute',
            dependencies=[Depends(RateLimiter(times=12, seconds=60))]
            )
async def read_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function returns a contact by ID for the current user.

    :param contact_id: The contact ID to retrieve.
    :type contact_id: int
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The contact with the provided contact ID or raises HTTP 404 if not found.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.get_contact(contact_id,  current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/",
             response_model=ContactResponse,
             status_code=status.HTTP_201_CREATED,
             description='No more than 12 requests per minute',
             dependencies=[Depends(RateLimiter(times=12, seconds=60))])
async def create_contact(
        body: ContactCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function creates a new contact for the current user.

    :param body: The contact's creation data.
    :type body: ContactCreate
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The newly created contact.
    :rtype: ContactResponse
    """
    return await repository_contacts.create_contact(body,  current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
        body: ContactUpdate,
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function updates an existing contact by ID for the current user.

    :param body: The updated contact data.
    :type body: ContactUpdate
    :param contact_id: The contact ID to update.
    :type contact_id: int
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The updated contact or raises HTTP 404 if not found.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.update_contact(contact_id, body,  current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    """
    The function removes a contact by ID for the current user.

    :param contact_id: The contact ID to remove.
    :type contact_id: int
    :param db: A database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The removed contact or raises HTTP 404 if not found.
    :rtype: ContactResponse
    """
    contact = await repository_contacts.remove_contact(contact_id,  current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
