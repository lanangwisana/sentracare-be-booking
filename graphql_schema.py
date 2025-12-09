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
    def bookings(self) -> List[BookingType]:
        db = SessionLocal()
        try:
            records = db.query(Booking).all()
            return [BookingType.from_model(b) for b in records]
        finally:
            db.close()

schema = strawberry.Schema(query=Query)