# sentracare-be-booking/graphql_schema.py
import strawberry
from typing import List, Optional
from models import Booking

@strawberry.type
class BookingType:
    id: int
    namaLengkap: str
    jenisLayanan: str
    tanggalPemeriksaan: str
    jamPemeriksaan: str
    status: str
    doctorName: Optional[str]

    @staticmethod
    def from_model(model: Booking) -> "BookingType":
        # Ambil nilai string murni dari Enum
        status_val = model.status.value if hasattr(model.status, "value") else str(model.status)
        layanan_val = model.jenis_layanan.value if hasattr(model.jenis_layanan, "value") else str(model.jenis_layanan)
        
        return BookingType(
            id=model.id,
            namaLengkap=model.nama_lengkap,
            jenisLayanan=layanan_val.replace("_", " ").title(), # Ubah MEDICAL_CHECKUP jadi Medical Checkup
            tanggalPemeriksaan=str(model.tanggal_pemeriksaan),
            jamPemeriksaan=str(model.jam_pemeriksaan),
            status=status_val.capitalize(), # Ubah PENDING jadi Pending
            doctorName=model.doctor_name
        )

@strawberry.type
class Query:
    @strawberry.field
    def bookings(self, info) -> List[BookingType]:
        from database import SessionLocal
        db = SessionLocal()
        try:
            request = info.context["request"]
            user = getattr(request.state, "user", None)
            if not user: return []
            
            query = db.query(Booking)
            # Samakan role dengan yang ada di DB (Uppercase)
            if user.get("role").upper() != "SUPERADMIN":
                query = query.filter(Booking.email == user.get("email"))
            
            records = query.order_by(Booking.id.desc()).all()
            return [BookingType.from_model(b) for b in records]
        finally:
            db.close()

schema = strawberry.Schema(query=Query)