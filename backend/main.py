from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Ticket
from schemas import TicketCreate, TicketOut
from service import create_ticket
from ml_client import MlClient

Base.metadata.create_all(bind=engine)

app = FastAPI(title="StringTheory Backend", version="1.0.0")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- Health ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ml-health")
def ml_health():
    return MlClient().health()


# ---------- CRUD ----------
@app.post("/api/tickets", response_model=TicketOut)
def create(payload: TicketCreate, db: Session = Depends(get_db)):
    return create_ticket(db, payload)


@app.get("/api/tickets", response_model=list[TicketOut])
def list_tickets(category: str | None = None, db: Session = Depends(get_db)):
    q = db.query(Ticket)
    if category:
        q = q.filter(Ticket.ml_category == category)
    return q.order_by(Ticket.id.desc()).all()


@app.get("/api/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "Not found")
    return t


@app.patch("/api/tickets/{ticket_id}/assign")
def assign(ticket_id: int, assignee: str, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "Not found")
    t.assignee = assignee
    t.status = "IN_PROGRESS"
    db.commit()
    return {"ok": True}


@app.patch("/api/tickets/{ticket_id}/close")
def close(ticket_id: int, db: Session = Depends(get_db)):
    t = db.get(Ticket, ticket_id)
    if not t:
        raise HTTPException(404, "Not found")
    t.status = "CLOSED"
    db.commit()
    return {"ok": True}


# ---------- Static / UI ----------
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")