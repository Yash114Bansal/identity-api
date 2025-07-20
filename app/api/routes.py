from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.contact import ContactCreate, ContactResponse
from app.services.contact_service import ContactService
from app.db.session import DBSessionManager

router = APIRouter()

def get_db():
    db_manager = DBSessionManager()
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

@router.post("/identify", response_model=ContactResponse, status_code=status.HTTP_200_OK)
def identify_contact(
    contact_in: ContactCreate,
    db: Session = Depends(get_db)
):
    service = ContactService(db)
    return service.identify_contact(contact_in)
