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
            
            if not user: 
                print("DEBUG: No user found in request state")
                return []
            
            # Ambil role dan pastikan tidak None sebelum di .upper()
            user_role = str(user.get("role", "")).upper()
            user_email = user.get("email")

            query = db.query(Booking)
            
            # Logika: Jika BUKAN SuperAdmin, baru di-filter emailnya
            if user_role != "SUPERADMIN":
                query = query.filter(Booking.email == user_email)
            
            records = query.order_by(Booking.id.desc()).all()
            print(f"DEBUG: Found {len(records)} bookings for role {user_role}")
            return [BookingType.from_model(b) for b in records]
        finally:
            db.close()

schema = strawberry.Schema(query=Query)