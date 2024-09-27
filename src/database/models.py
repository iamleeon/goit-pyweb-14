from sqlalchemy import Column, Integer, String, Date, func, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    created_at = Column('created_at', DateTime, default=func.now())
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(320), nullable=False, unique=True)
    phone = Column(String(15), nullable=False)
    birthday = Column("birthday", Date, nullable=False)
    additional_info = Column(String(350), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="contacts")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(320), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column("created_at", DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    contacts = relationship("Contact", back_populates="user")
    confirmed = Column(Boolean, default=False)
