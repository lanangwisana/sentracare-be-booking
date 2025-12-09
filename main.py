# bagian main ini digunakan sebagai entry point FastAPI 
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Booking, StatusEnum
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time
from schemas import BookingRequest, BookingResponse
from models import JenisKelaminEnum, JenisLayananEnum, TipeLayananEnum
import strawberry
from strawberry.fastapi import GraphQLRouter

class BookingSuccessResponse(BaseModel):
    message: str
    booking: BookingResponse

    class Config:
        orm_mode = True
@strawberry.type
class BookingType:
    id: int
    nama_lengkap: str
    jenis_layanan: str
    tanggal_pemeriksaan: str
    jam_pemeriksaan: str
    status: str
@strawberry.type
class Query:
    @strawberry.field
    def bookings(self, info) -> list[BookingType]:
        db = SessionLocal()
        try:
            return db.query(Booking).all()
        finally:
            db.close()
schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

# Konfigurasi CORS (Cross-Origin Resource Sharing)
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

# Endpoint untuk membuat booking baru
@app.post("/booking", response_model=BookingSuccessResponse)
def create_booking(data: BookingRequest, db: Session = Depends(get_db)):
    booking = Booking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {"message": "Booking berhasil", "booking": booking}

# Endpoint untuk mendapatkan daftar semua booking
@app.get("/booking", response_model=list[BookingResponse])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(Booking).all()

# Endpoint untuk memperbarui status booking
@app.put("/booking/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(booking_id: int, status: StatusEnum, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking tidak ditemukan")
    booking.status = status
    db.commit()
    db.refresh(booking)
    return booking

