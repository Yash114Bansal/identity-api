from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator

class ContactBase(BaseModel):
    email: Optional[EmailStr] = None
    phoneNumber: Optional[str] = None

class ContactCreate(ContactBase):
    pass

class ContactResponse(BaseModel):
    primaryContatctId: int
    emails: List[str]
    phoneNumbers: List[str]
    secondaryContactIds: List[int]

    class Config:
        orm_mode = True
