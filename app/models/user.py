from sqlalchemy import Boolean, Column, String, Date, Integer, Enum
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    nationality = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    position = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"