import strawberry
from typing import List
from models import Booking
from database import SessionLocal

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
            jenis_layanan=model.jenis_layanan.value if hasattr(model.jenis_layanan, "value") else model.jenis_layanan,
            tanggal_pemeriksaan=str(model.tanggal_pemeriksaan),
            jam_pemeriksaan=str(model.jam_pemeriksaan),
            status=model.status.value if hasattr(model.status, "value") else model.status,
        )

@strawberry.type
class Query:
    @strawberry.field
    def bookings(self, info, status: str | None = None) -> List[BookingType]:
        db = SessionLocal()
        user = getattr(info.context["request"].state, "user", None)
        query = db.query(Booking)

        if not user:
            return []

        if user["role"] != "SuperAdmin":
            query = query.filter(Booking.email == user["email"])

        if status:
            query = query.filter(Booking.status == status)

        return [BookingType.from_model(b) for b in query.all()]

@strawberry.type
class Mutation:
    @strawberry.mutation
    def updateBookingStatus(self, id: int, status: str, info) -> BookingType:
        user = getattr(info.context["request"].state, "user", None)
        if not user or user["role"] != "SuperAdmin":
            raise Exception("Unauthorized")
        db = SessionLocal()
        booking = db.query(Booking).get(id)
        if not booking:
            raise Exception("Not found")
        booking.status = status
        db.commit()
        db.refresh(booking)
        return BookingType.from_model(booking)

