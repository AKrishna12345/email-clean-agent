from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Float,
    Enum,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from enum import Enum as PyEnum
import config

# Create database engine
engine = create_engine(config.DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=False)  # Encrypted
    token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (useful for navigating / querying runs and email items)
    email_runs = relationship("EmailRun", back_populates="user", cascade="all, delete-orphan")
    email_items = relationship("EmailItem", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email={self.email})>"


class EmailRunStatus(str, PyEnum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EmailItemStatus(str, PyEnum):
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class EmailRun(Base):
    """
    A single "clean" run request by a user.
    Tracks lifecycle/status and timing; per-email work is tracked in EmailItem.
    """

    __tablename__ = "email_runs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    status = Column(Enum(EmailRunStatus), nullable=False, default=EmailRunStatus.NEW, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)

    # Optional: store a human-readable error for FAILED runs
    error = Column(Text, nullable=True)

    user = relationship("User", back_populates="email_runs")
    email_items = relationship("EmailItem", back_populates="run", cascade="all, delete-orphan")


class EmailItem(Base):
    """
    A Gmail message tracked by the system.

    Global-per-user uniqueness is enforced by (user_id, gmail_message_id).
    """

    __tablename__ = "email_items"
    __table_args__ = (
        UniqueConstraint("user_id", "gmail_message_id", name="uq_email_items_user_gmail_message_id"),
    )

    id = Column(Integer, primary_key=True, index=True)

    # Needed for "global per user" idempotency
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Links the item to the run that ingested it
    run_id = Column(Integer, ForeignKey("email_runs.id"), nullable=False, index=True)

    # Gmail message id from the Gmail API
    gmail_message_id = Column(String, nullable=False)

    # Processing state machine
    status = Column(Enum(EmailItemStatus), nullable=False, default=EmailItemStatus.NEW, index=True)

    # Classification output
    category = Column(String, nullable=True, index=True)
    confidence = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="email_items")
    run = relationship("EmailRun", back_populates="email_items")


# Create all tables - if already exists, it will not create again
def init_db():
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

