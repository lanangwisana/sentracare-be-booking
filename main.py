import os
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
from typing import List, Optional
from schemas import BookingRequest, UpdateStatusRequest
from datetime import date
import httpx

# SECRET_KEY harus sama dengan Auth Service
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "changeme")
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ISSUER = os.getenv("AUTH_ISSUER", "sentracare-auth")
AUDIENCE = os.getenv("AUTH_AUDIENCE", "sentracare-services")

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

# === Helper Functions ===
def calculate_age(dob: Optional[date]) -> int:
    if not dob:
        return 0
    today = date.today()
    age = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1
    return max(age, 0)

def gender_full_from_booking(booking: Booking) -> str:
    if booking.jenis_kelamin and booking.jenis_kelamin.value == "PEREMPUAN":
        return "Perempuan"
    return "Laki-laki"

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
            email=user.get("email"),
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
async def update_booking_status(booking_id: int, data: UpdateStatusRequest, request: Request, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking tidak ditemukan")

    status_input = data.status.upper()
    try:
        if status_input == "CONFIRMED":
            booking.status = StatusEnum.CONFIRMED
            # PERBAIKAN: Gunakan data.doctor_name (BUKAN data.get)
            booking.doctor_name = data.doctor_name
            
            # --- LOGIKA OTOMATISASI PARALEL (Push ke Patient Service) ---
            age = calculate_age(booking.tanggal_lahir)
            gender_full = gender_full_from_booking(booking)

            patient_payload = {
                "full_name": booking.nama_lengkap,
                "email": booking.email,
                "phone_number": booking.nomor_telepon,
                "gender": gender_full,  
                "age": age,
                "address": booking.alamat,
                "tipe_layanan": booking.tipe_layanan.value if booking.tipe_layanan else "",
                "tanggal_pemeriksaan": str(booking.tanggal_pemeriksaan) if booking.tanggal_pemeriksaan else None,
                "jam_pemeriksaan": str(booking.jam_pemeriksaan) if booking.jam_pemeriksaan else None,
                "doctor_name": data.doctor_name, 
                "doctor_email": data.doctor_email,
                "booking_id": booking.id
            }
            
            async with httpx.AsyncClient() as client:
                try:
                    await client.post("http://patient-service:8000/patients/internal-register", json=patient_payload)
                except Exception as e:
                    print(f"Gagal push ke EMR: {e}")
        
        elif status_input == "CANCELLED":
            booking.status = StatusEnum.CANCELLED
        
        db.commit()
        db.refresh(booking)
        return booking
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

Base.metadata.create_all(bind=engine)


class BookingResponse(BaseModel):
    id: int
    nama_lengkap: str
    tanggal_lahir: Optional[date]
    jenis_kelamin: str
    nomor_telepon: Optional[str]
    email: str
    alamat: Optional[str]
    jenis_layanan: str
    tipe_layanan: Optional[str]
    tanggal_pemeriksaan: date
    jam_pemeriksaan: str
    catatan: Optional[str]
    status: str
    doctor_name: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    
    class Config:
        from_attributes = True
        
# Endpoint baru untuk mendapatkan data booking lengkap
@app.get("/api/bookings/full", response_model=List[BookingResponse])
async def get_full_bookings(request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = db.query(Booking)
    if user.get("role").upper() != "SUPERADMIN":
        query = query.filter(Booking.email == user.get("email"))
    
    bookings = query.order_by(Booking.id.desc()).all()
    
    result = []
    for booking in bookings:
        booking_dict = {
            "id": booking.id,
            "nama_lengkap": booking.nama_lengkap,
            "tanggal_lahir": booking.tanggal_lahir,
            "jenis_kelamin": booking.jenis_kelamin.value if booking.jenis_kelamin else None,
            "nomor_telepon": booking.nomor_telepon,
            "email": booking.email,
            "alamat": booking.alamat,
            "jenis_layanan": booking.jenis_layanan.value if booking.jenis_layanan else None,
            "tipe_layanan": booking.tipe_layanan.value if booking.tipe_layanan else None,
            "tanggal_pemeriksaan": booking.tanggal_pemeriksaan,
            "jam_pemeriksaan": str(booking.jam_pemeriksaan) if booking.jam_pemeriksaan else None,
            "catatan": booking.catatan,
            "status": booking.status.value if booking.status else "PENDING",
            "doctor_name": booking.doctor_name,
            "created_at": str(booking.created_at) if booking.created_at else None,
            "updated_at": str(booking.updated_at) if booking.updated_at else None,
        }
        try:
            validated_booking = BookingResponse(**booking_dict)
            result.append(validated_booking)
        except Exception as e:
            print(f"Error validating booking {booking.id}: {e}")
    
    return result

# Endpoint khusus untuk patient service EMR
@app.get("/api/bookings/emr-patients", response_model=List[dict])
async def get_bookings_for_emr(request: Request, db: Session = Depends(get_db)):
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    query = db.query(Booking)
    if user.get("role").upper() != "SUPERADMIN":
        query = query.filter(Booking.email == user.get("email"))
