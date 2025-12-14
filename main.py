# bagian main ini digunakan sebagai entry point FastAPI 
from fastapi import FastAPI, Depends, HTTPException, Request
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
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-this-secret-in-prod")
ALGORITHM = "HS256"
AUDIENCE = os.getenv("AUTH_AUDIENCE", "sentracare-services")
ISSUER = os.getenv("AUTH_ISSUER", "sentracare-auth")

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
    @staticmethod
    def from_model(model: Booking) -> "BookingType":
        return BookingType(
            id=model.id,
            nama_lengkap=model.nama_lengkap,
            # Perlu handle Enum jika jenis_layanan atau status adalah Enum
            jenis_layanan=model.jenis_layanan.value if hasattr(model.jenis_layanan, "value") else model.jenis_layanan,
            tanggal_pemeriksaan=str(model.tanggal_pemeriksaan),
            jam_pemeriksaan=str(model.jam_pemeriksaan),
            status=model.status.value if hasattr(model.status, "value") else model.status,
        )
@strawberry.type
class Query:
    @strawberry.field
    def bookings(self, info) -> list[BookingType]:
        db = SessionLocal()
        try:
            user = getattr(info.context["request"].state, "user", None)
            if not user:
                return [] 
            query = db.query(Booking)
            if user["role"] != "SuperAdmin":
                user_email = user.get("email")
                if user_email:
                    query = query.filter(Booking.email == user_email)
                else:
                    return []
            query = query.order_by(Booking.created_at.desc())

            return [BookingType.from_model(b) for b in query.all()]
        finally:
            db.close()
schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
@app.middleware("http")
async def add_user_to_request(request: Request, call_next):
    auth = request.headers.get("Authorization")
    print("Authorization header:", auth)
    request.state.user = None
    if auth and auth.startswith("Bearer "):
        token = auth.split(" ")[1]
        try:
            claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=AUDIENCE, issuer=ISSUER) 
            request.state.user = {
                "email": claims.get("email"),
                "role": claims.get("role"),
            }
            print("Decoded JWT claims:", claims)
            print("Request user set to:", request.state.user)
        except JWTError:
            request.state.user = None
    return await call_next(request)

app.include_router(graphql_app, prefix="/graphql")

# Konfigurasi CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://0.0.0.0:3000",
        "http://host.docker.internal:3000"],
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
async def create_booking(data: BookingRequest, request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    booking = Booking(
        **data.model_dump(),
        email=user["email"],   # simpan email dari JWT
        status=StatusEnum.PENDING,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {"message": "Booking berhasil", "booking": booking}

# Endpoint untuk mendapatkan daftar semua booking
@app.get("/booking", response_model=list[BookingResponse])
def list_bookings(request: Request, db: Session = Depends(get_db)):
    user = request.state.user
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    query = db.query(Booking)
    if user["role"] != "SuperAdmin":
        query = query.filter(Booking.email == user["email"])

    return query.order_by(Booking.created_at.desc()).all()


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

