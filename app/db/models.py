from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import String, Integer, ForeignKey


class Base(DeclarativeBase):
    pass

class Blob(Base):
    __tablename__ = 'blobs'
    id: Mapped[int] = mapped_column(primary_key=True)
    hash: Mapped[str] = mapped_column(String, unique=True)
    size_bytes: Mapped[int] = mapped_column(Integer)

    files = relationship("File", back_populates="blob")


class File(Base):
    __tablename__ = 'files'
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_sub: Mapped[str] = mapped_column(String)
    display_name: Mapped[str] = mapped_column(String)
    blob_id: Mapped[int] = mapped_column(ForeignKey('blobs.id'))
    
    blob = relationship("Blob", back_populates="files")


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    sub: Mapped[str] = mapped_column(String)
    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
