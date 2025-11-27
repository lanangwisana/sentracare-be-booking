from pydantic import BaseModel, EmailStr
from datetime import date, time
from typing import Optional
from enum import Enum

# Enum untuk validasi pilihan dropdown
class JenisKelaminEnum(str, Enum):
    LAKI_LAKI = "Laki-laki"
    PEREMPUAN = "Perempuan"

class JenisLayananEnum(str, Enum):
    MEDICAL_CHECKUP = "Medical Check-Up"
    VAKSINASI = "Vaksinasi"
    LAB_TES = "Lab Tes"

class TipeLayananEnum(str, Enum):
    FULL_BODY = "Madical Check-Up Full Body"
    HPV = "Vaksinasi HPV"
    ANAK_BAYI = "Vaksinasi Anak & Bayi"
    TES_DARAH = "Tes Darah"
    TES_HORMON = "Tes Hormon"
    TES_URINE = "Tes Urine"

# Schema untuk request body
class BookingRequest(BaseModel):
    nama_lengkap: str
    tanggal_lahir: date
    jenis_kelamin: JenisKelaminEnum
    nomor_telepon: str
    email: EmailStr
    alamat: str
    jenis_layanan: JenisLayananEnum
    tipe_layanan: TipeLayananEnum
    tanggal_pemeriksaan: date
    jam_pemeriksaan: time
    catatan: Optional[str] = None

# Schema untuk response
class BookingResponse(BaseModel):
    id: int
    nama_lengkap: str
    jenis_kelamin: JenisKelaminEnum
    jenis_layanan: JenisLayananEnum
    tipe_layanan: TipeLayananEnum
    tanggal_pemeriksaan: date
    jam_pemeriksaan: time
    catatan: Optional[str] = None

    class Config:
        orm_mode = True
