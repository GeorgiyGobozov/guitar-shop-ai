from sqlalchemy.orm import Session

from models import Ticket
from schemas import TicketCreate
from ml_client import MlClient

ml = MlClient()


def create_ticket(db: Session, payload: TicketCreate) -> Ticket:
    ticket = Ticket(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        subject=payload.subject,
        description=payload.description,
        status="NEW",
    )

    text_for_ml = f"{payload.subject}. {payload.description}"
    pred = ml.predict(text_for_ml)

    if pred:
        ticket.ml_category = pred["category"]["label"]
        ticket.ml_priority = pred["priority"]["label"]
        ticket.ml_problem_type = pred["problem_type"]["label"]
        ticket.ml_confidence = round(
            (pred["category"]["confidence"]
             + pred["priority"]["confidence"]
             + pred["problem_type"]["confidence"]) / 3,
            3,
        )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket