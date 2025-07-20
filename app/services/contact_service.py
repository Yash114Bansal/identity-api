from sqlalchemy.orm import Session
from app.models.contact import Contact, LinkPrecedenceEnum
from app.schemas.contact import ContactCreate, ContactResponse
from typing import List, Optional, Set
from sqlalchemy import or_, and_
from app.core.exceptions import InvalidContactInput

class ContactService:
    """
    Service class for handling business logic related to customer contact identification and linking.
    Implements rules for primary/secondary contacts and merging logic.
    """
    def __init__(self, db: Session):
        """Initialize the service with a database session."""
        self.db = db

    def identify_contact(self, contact_in: ContactCreate) -> ContactResponse:
        """
        Identify or create a customer contact based on email and/or phone number.
        Handles linking, merging, and secondary creation as per business rules.
        """
        if not contact_in.email and not contact_in.phoneNumber:
            raise InvalidContactInput()
        # find all contacts with matching email or phone
        contacts = self.db.query(Contact).filter(
            or_(
                Contact.email == contact_in.email if contact_in.email else False,
                Contact.phoneNumber == contact_in.phoneNumber if contact_in.phoneNumber else False
            )
        ).all()
        if not contacts:
            # No existing contact, create new primary one
            new_contact = Contact(
                email=contact_in.email,
                phoneNumber=contact_in.phoneNumber,
                linkPrecedence=LinkPrecedenceEnum.primary
            )
            self.db.add(new_contact)
            self.db.commit()
            self.db.refresh(new_contact)
            return ContactResponse(
                primaryContatctId=new_contact.id,
                emails=[new_contact.email] if new_contact.email else [],
                phoneNumbers=[new_contact.phoneNumber] if new_contact.phoneNumber else [],
                secondaryContactIds=[]
            )
        # find all related contacts (by email or phone, recursively)
        all_related_contacts = set(contacts)
        to_check = set(contacts)
        while to_check:
            current = to_check.pop()
            linked = self.db.query(Contact).filter(
                or_(
                    Contact.linkedId == current.id,
                    Contact.id == current.linkedId
                )
            ).all()
            new_contacts = set(linked) - all_related_contacts
            all_related_contacts.update(new_contacts)
            to_check.update(new_contacts)
        all_related_contacts = list(all_related_contacts)
        # find all primaries ones
        primaries = [c for c in all_related_contacts if c.linkPrecedence == LinkPrecedenceEnum.primary]
        if primaries:
            primary = min(primaries, key=lambda c: c.createdAt)
        else:
            primary = min(all_related_contacts, key=lambda c: c.createdAt)
        # if there are multiple primaries, update all but the oldest to secondary
        for p in primaries:
            if p.id != primary.id:
                p.linkPrecedence = LinkPrecedenceEnum.secondary
                p.linkedId = primary.id
                self.db.add(p)
        self.db.commit()
        # gather all linked contacts (primary + secondaries)
        all_linked = self.db.query(Contact).filter(
            or_(
                Contact.id == primary.id,
                Contact.linkedId == primary.id
            )
        ).all()
        # Check if new info needs to be added as secondary
        emails: Set[str] = set([c.email for c in all_linked if c.email])
        phoneNumbers: Set[str] = set([c.phoneNumber for c in all_linked if c.phoneNumber])
        secondaryContactIds = [c.id for c in all_linked if c.linkPrecedence == LinkPrecedenceEnum.secondary]
        is_new_info = False
        if contact_in.email and contact_in.email not in emails:
            is_new_info = True
        if contact_in.phoneNumber and contact_in.phoneNumber not in phoneNumbers:
            is_new_info = True
        if is_new_info:
            new_secondary = Contact(
                email=contact_in.email,
                phoneNumber=contact_in.phoneNumber,
                linkedId=primary.id,
                linkPrecedence=LinkPrecedenceEnum.secondary
            )
            self.db.add(new_secondary)
            self.db.commit()
            self.db.refresh(new_secondary)
            secondaryContactIds.append(new_secondary.id)
            if new_secondary.email:
                emails.add(new_secondary.email)
            if new_secondary.phoneNumber:
                phoneNumbers.add(new_secondary.phoneNumber)
        # Always return primary info first
        emails = [primary.email] + [e for e in emails if e != primary.email]
        phoneNumbers = [primary.phoneNumber] + [p for p in phoneNumbers if p != primary.phoneNumber]
        return ContactResponse(
            primaryContatctId=primary.id,
            emails=emails,
            phoneNumbers=phoneNumbers,
            secondaryContactIds=secondaryContactIds
        )
