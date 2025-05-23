from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import re

class ClientBase(BaseModel):
    name: str
    email: EmailStr
    cpf: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = True

    @validator('cpf')
    def cpf_validator(cls, v):
        # Remove non-numeric characters
        cpf = re.sub(r'[^0-9]', '', v)
        
        # Check if CPF has 11 digits
        if len(cpf) != 11:
            raise ValueError('CPF must have 11 digits')
        
        # Check if all digits are the same (invalid CPF)
        if cpf == cpf[0] * 11:
            raise ValueError('Invalid CPF')
        
        # Validate CPF algorithm
        # Calculate first check digit
        total = 0
        for i in range(9):
            total += int(cpf[i]) * (10 - i)
        remainder = total % 11
        check_digit_1 = 0 if remainder < 2 else 11 - remainder
        
        if int(cpf[9]) != check_digit_1:
            raise ValueError('Invalid CPF')
        
        # Calculate second check digit
        total = 0
        for i in range(10):
            total += int(cpf[i]) * (11 - i)
        remainder = total % 11
        check_digit_2 = 0 if remainder < 2 else 11 - remainder
        
        if int(cpf[10]) != check_digit_2:
            raise ValueError('Invalid CPF')
        
        # Format CPF for display
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    @validator('phone')
    def phone_validator(cls, v):
        # Remove non-numeric characters
        phone = re.sub(r'[^0-9]', '', v)
        
        # Check if phone number has at least 10 digits (area code + number)
        if len(phone) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        
        # Format phone for display if it has 11 digits (with 9 prefix)
        if len(phone) == 11:
            return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
        # Format phone for display if it has 10 digits
        elif len(phone) == 10:
            return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
        
        return phone

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True

class ClientInDBBase(ClientBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

    class Config:
        orm_mode = True

class Client(ClientInDBBase):
    pass