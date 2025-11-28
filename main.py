# bagian main ini digunakan sebagai entry point FastAPI 
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Booking
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time
from schemas import BookingRequest, BookingResponse
from models import JenisKelaminEnum, JenisLayananEnum, TipeLayananEnum

class BookingSuccessResponse(BaseModel):
    message: str
    booking: BookingResponse

    class Config:
        orm_mode = True

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/booking", response_model=BookingSuccessResponse)
def create_booking(data: BookingRequest, db: Session = Depends(get_db)):
    booking = Booking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Booking berhasil", "booking": booking}

