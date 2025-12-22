# sentracare-be-booking/models.py
from enum import Enum
from sqlalchemy import Column, Integer, String, Date, Time, Text, DateTime, Enum as SqlEnum
from sqlalchemy.sql import func
from database import Base

class JenisKelaminEnum(str, Enum):
    LAKI_LAKI = "LAKI_LAKI"
    PEREMPUAN = "PEREMPUAN"

class JenisLayananEnum(str, Enum):
    MEDICAL_CHECKUP = "MEDICAL_CHECKUP" # Harus UPPERCASE sesuai pesan error
    VAKSINASI = "VAKSINASI"
    LAB_TES = "LAB_TES"

class TipeLayananEnum(str, Enum):
    FULL_BODY = "FULL_BODY"
    HPV = "HPV"
    ANAK_BAYI = "ANAK_BAYI"
    TES_DARAH = "TES_DARAH"
    TES_HORMON = "TES_HORMON"
    TES_URINE = "TES_URINE"
    
class StatusEnum(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    nama_lengkap = Column(String(100))
    tanggal_lahir = Column(Date)
    jenis_kelamin = Column(SqlEnum(JenisKelaminEnum))
    nomor_telepon = Column(String(20))
    email = Column(String(100))
    alamat = Column(Text)
    jenis_layanan = Column(SqlEnum(JenisLayananEnum))
    tipe_layanan = Column(SqlEnum(TipeLayananEnum))
    tanggal_pemeriksaan = Column(Date)
    jam_pemeriksaan = Column(Time)
    catatan = Column(Text, nullable=True)
    status = Column(SqlEnum(StatusEnum), default=StatusEnum.PENDING)
    doctor_name = Column(String(100), nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())