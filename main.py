# bagian main ini digunakan sebagai entry point FastAPI 
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Booking
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time

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

class BookingRequest(BaseModel):
    nama_lengkap: str
    tanggal_lahir: date
    jenis_kelamin: JenisKelaminEnum
    nomor_telepon: str
    email: EmailStr
    alamat: str
    jenis_layanan: JenisLayananEnum
    tipe_layanan: TipeLayananEnum
    tanggal_pemeriksaan: date
    jam_pemeriksaan: time
    catatan: Optional[str] = None

@app.post("/booking")
def create_booking(data: BookingRequest, db: Session = Depends(get_db)):
    booking = Booking(**data.dict())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Booking berhasil", "id": booking.id}
