import strawberry
from typing import List
from models import Booking, StatusEnum
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
    def updateBookingStatus(self, info, id: int, status: str) -> BookingType:
        db = SessionLocal()
        try:
            user = getattr(info.context["request"].state, "user", None)
            # Cek autentikasi dan authorization
            if not user:
                raise Exception("Unauthorized: User not authenticated")
            if user["role"] != "SuperAdmin":
                raise Exception("Unauthorized: Only SuperAdmin can update booking status")
            # Cari booking
            booking = db.query(Booking).filter(Booking.id == id).first()
            if not booking:
                raise Exception(f"Booking with id {id} not found")
            try:
                # Konversi ke uppercase untuk mencocokkan enum
                status_upper = status.upper()
                if status_upper == "CONFIRMED":
                    status_enum = StatusEnum.CONFIRMED
                elif status_upper == "CANCELLED":
                    status_enum = StatusEnum.CANCELLED
                elif status_upper == "PENDING":
                    status_enum = StatusEnum.PENDING
                else:
                    raise Exception(f"Invalid status: {status}")
            except ValueError:
                raise Exception(f"Invalid status value: {status}")
            # Update status
            booking.status = status_enum
            db.commit()
            db.refresh(booking)
            
            return BookingType.from_model(booking)
        except Exception as e:
            db.rollback()
            raise e  # Re-raise exception agar GraphQL bisa menangkapnya
        finally:
            db.close()

# Export schema
schema = strawberry.Schema(query=Query, mutation=Mutation)