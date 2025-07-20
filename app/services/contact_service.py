from sqlalchemy.orm import Session
from app.models.contact import Contact, LinkPrecedenceEnum
from app.schemas.contact import ContactCreate, ContactResponse
from typing import List, Optional
from sqlalchemy import or_, and_

class ContactService:
    def __init__(self, db: Session):
        self.db = db

    def identify_contact(self, contact_in: ContactCreate) -> ContactResponse:
        # find all contacts with matching email or phone
        query = self.db.query(Contact).filter(
            or_(
                Contact.email == contact_in.email if contact_in.email else False,
                Contact.phoneNumber == contact_in.phoneNumber if contact_in.phoneNumber else False
            )
        )
        contacts = query.all()

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

        # There are existing contacts, find the primary one
        primaries = [c for c in contacts if c.linkPrecedence == LinkPrecedenceEnum.primary]
        if primaries:
            primary = min(primaries, key=lambda c: c.createdAt)
        else:
            primary = min(contacts, key=lambda c: c.createdAt)

        # Gather all linked contacts (primary + secondaries)
        all_linked = self.db.query(Contact).filter(
            or_(
                Contact.id == primary.id,
                Contact.linkedId == primary.id
            )
        ).all()

        # Check if new info needs to be added as secondary
        emails = set([c.email for c in all_linked if c.email])
        phoneNumbers = set([c.phoneNumber for c in all_linked if c.phoneNumber])
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
