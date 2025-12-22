# sentracare-be-booking/main.py
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Booking, StatusEnum
import strawberry
from strawberry.fastapi import GraphQLRouter
from jose import jwt, JWTError
from graphql_schema import schema
from pydantic import BaseModel
from typing import Optional
from schemas import BookingRequest, UpdateStatusRequest

# SECRET_KEY harus sama dengan Auth Service
SECRET_KEY = "sentracare-rahasia-sangat-aman-123"
ALGORITHM = "HS256"
AUDIENCE = "sentracare-services"
ISSUER = "sentracare-auth"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    auth = request.headers.get("Authorization")
    request.state.user = None
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
        try:
            claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER) 
            request.state.user = claims
        except JWTError:
            request.state.user = None
    return await call_next(request)

# === ENDPOINT UNTUK PASIEN MEMBUAT BOOKING ===
@app.post("/booking")
async def create_booking(data: BookingRequest, request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Sesi berakhir, silakan login ulang")

    try:
        new_booking = Booking(
            nama_lengkap=data.nama_lengkap,
            tanggal_lahir=data.tanggal_lahir,
            jenis_kelamin=data.jenis_kelamin,
            nomor_telepon=data.nomor_telepon,
            email=user.get("email"), # Email otomatis diambil dari Token JWT Login
            alamat=data.alamat,
            jenis_layanan=data.jenis_layanan,
            tipe_layanan=data.tipe_layanan,
            tanggal_pemeriksaan=data.tanggal_pemeriksaan,
            jam_pemeriksaan=data.jam_pemeriksaan,
            catatan=data.catatan,
            status=StatusEnum.PENDING
        )
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
        return {"message": "Booking berhasil", "booking": new_booking}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/booking/{booking_id}/status")
async def update_booking_status(booking_id: int, data: UpdateStatusRequest, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking tidak ditemukan")
    
    status_input = data.status.upper()
    try:
        if status_input == "CONFIRMED":
            booking.status = StatusEnum.CONFIRMED
            booking.doctor_name = data.doctor_name
        elif status_input == "CANCELLED":
            booking.status = StatusEnum.CANCELLED
        
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

Base.metadata.create_all(bind=engine)