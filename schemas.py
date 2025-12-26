# sentracare-be-booking/schemas.py
from pydantic import BaseModel
from datetime import date, time
from typing import Optional
from models import JenisKelaminEnum, JenisLayananEnum, TipeLayananEnum

class BookingRequest(BaseModel):
    nama_lengkap: str
    tanggal_lahir: date
    jenis_kelamin: JenisKelaminEnum
    nomor_telepon: str
    alamat: str
    jenis_layanan: JenisLayananEnum
    tipe_layanan: Optional[TipeLayananEnum] = None
    tanggal_pemeriksaan: date
    jam_pemeriksaan: time
    catatan: Optional[str] = None

class UpdateStatusRequest(BaseModel):
    status: str
    doctor_name: Optional[str] = None
    doctor_email: Optional[str] = None 