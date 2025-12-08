# Bagian models.py ini dugunakan untuk membuat struktur tabel booking di database
from enum import Enum
from sqlalchemy import Column, Integer, String, Date, Time, Text, DateTime, Enum as SqlEnum
from sqlalchemy.sql import func
from database import Base

class JenisKelaminEnum(str, Enum):
    LAKI_LAKI = "Laki-laki"
    PEREMPUAN = "Perempuan"

class JenisLayananEnum(str, Enum):
    MEDICAL_CHECKUP = "Medical Check-Up"
    VAKSINASI = "Vaksinasi"
    LAB_TES = "Lab Tes"

class TipeLayananEnum(str, Enum):
    FULL_BODY = "Medical Check-Up Full Body"
    HPV = "Vaksinasi HPV"
    ANAK_BAYI = "Vaksinasi Anak & Bayi"
    TES_DARAH = "Tes Darah"
    TES_HORMON = "Tes Hormon"
    TES_URINE = "Tes Urine"
    
class StatusEnum(str, Enum):
    PENDING = "Pending"
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"

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
    catatan = Column(Text, nullable= True)
    status = Column(SqlEnum(StatusEnum), default=StatusEnum.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
