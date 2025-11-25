# bagian main ini digunakan sebagai entry point FastAPI 
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Booking
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookingRequest(BaseModel):
    nama_lengkap: str
    tanggal_lahir: date
    jenis_kelamin: str
    nomor_telepon: str
    email: EmailStr
    alamat: str
    jenis_layanan: str
    tipe_layanan: Optional[str]
    tanggal_pemeriksaan: date
    jam_pemeriksaan: time
    catatan: Optional[str]

@app.post("/booking")
def create_booking(data: BookingRequest, db: Session = Depends(get_db)):
    booking = Booking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Booking berhasil", "id": booking.id}
