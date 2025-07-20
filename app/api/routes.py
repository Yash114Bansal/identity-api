from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService
from app.db.session import DBSessionManager

router = APIRouter()

def get_db():
    """Dependency to get a database session."""
    db_manager = DBSessionManager()
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/identify",
    response_model=ContactResponse,
    status_code=status.HTTP_200_OK,
    summary="Identify or create a customer contact",
    description="""
    Identifies a customer based on email and/or phone number. If the contact does not exist, creates a new primary contact. If the contact exists, returns the consolidated contact information, linking as secondary if needed.
    """
)
def identify_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db)
):
    """Identify or create a customer contact and return the consolidated contact information."""
    service = ContactService(db)
    return service.identify_contact(contact_in)
