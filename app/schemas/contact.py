from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

class ContactBase(BaseModel):
    email: Optional[EmailStr] = Field(None, description="The email address of the contact.")
    phoneNumber: Optional[str] = Field(None, description="The phone number of the contact.")

class ContactCreate(ContactBase):
    """Schema for creating or identifying a contact."""
    pass

class ContactResponse(BaseModel):
    primaryContatctId: int = Field(..., description="The ID of the primary contact.")
    emails: List[str] = Field(..., description="List of all emails associated with the contact, primary first.")
    phoneNumbers: List[str] = Field(..., description="List of all phone numbers associated with the contact, primary first.")
    secondaryContactIds: List[int] = Field(..., description="IDs of all secondary contacts linked to the primary contact.")

    model_config = dict(from_attributes=True)
