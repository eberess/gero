from pydantic import BaseModel


class ContactCreate(BaseModel):
    name: str
    phone: str
    notes: str = ""


class ContactUpdate(BaseModel):
    name: str
    phone: str
    notes: str = ""


class SendSMSRequest(BaseModel):
    phone: str
    message: str
    device_id: str | None = None
    sim_number: int | None = None
    priority: int = 0


class SendSMSBatchRequest(BaseModel):
    phone_numbers: list[str]
    message: str
    device_id: str | None = None
    sim_number: int | None = None
    priority: int = 0
