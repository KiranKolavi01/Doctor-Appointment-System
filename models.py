from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    admin = "admin"
    doctor = "doctor"
    patient = "patient"

class ConsultationModeEnum(str, Enum):
    Online = "Online"
    Offline = "Offline"

class ShiftTypeEnum(str, Enum):
    Morning = "Morning"
    Evening = "Evening"
    Night = "Night"

class AppointmentStatusEnum(str, Enum):
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no-show"

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: RoleEnum

class SigninRequest(BaseModel):
    username: str
    password: str

class DoctorCreate(BaseModel):
    name: str
    speciality: str
    consultation_mode: ConsultationModeEnum
    consultation_fee: float = Field(..., gt=0)

class DoctorUpdate(BaseModel):
    name: str
    speciality: str
    consultation_mode: ConsultationModeEnum
    consultation_fee: float = Field(..., gt=0)
    is_active: int

class ShiftCreate(BaseModel):
    doctor_id: str
    date: str
    start_time: str
    end_time: str
    shift_type: ShiftTypeEnum
    mode: ConsultationModeEnum

class SlotGenerate(BaseModel):
    shift_id: str
    slot_duration_minutes: int

    @validator("slot_duration_minutes")
    def validate_duration(cls, v):
        if v not in [15, 20, 30]:
            raise ValueError("slot_duration_minutes must be 15, 20, or 30")
        return v

class StatusUpdate(BaseModel):
    status: AppointmentStatusEnum

class PrescriptionCreate(BaseModel):
    appointment_id: str
    diagnosis_notes: Optional[str] = None
    prescribed_medicines: Optional[str] = None
    follow_up_instructions: Optional[str] = None

class VideoLinkUpdate(BaseModel):
    video_link: str

class AppointmentBook(BaseModel):
    patient_id: str
    slot_id: str
