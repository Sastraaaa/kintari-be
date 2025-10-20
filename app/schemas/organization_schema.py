from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class OrganizationInfoSchema(BaseModel):
    id: Optional[int] = None
    name: str
    founded_date: Optional[str] = None
    ideology: Optional[str] = None
    legal_basis: Optional[str] = None
    objectives: Optional[str] = None
    summary: Optional[str] = None
    full_text: Optional[str] = None
    extracted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MembershipTypeSchema(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    type_name: str
    description: Optional[str] = None
    rights: Optional[str] = None
    obligations: Optional[str] = None

    class Config:
        from_attributes = True


class OrgStructureSchema(BaseModel):
    id: Optional[int] = None
    organization_id: Optional[int] = None
    level: str
    name: str
    parent_id: Optional[int] = None
    leader_name: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentSchema(BaseModel):
    id: Optional[int] = None
    filename: str
    file_path: Optional[str] = None
    document_type: str
    organization_id: Optional[int] = None
    file_size: Optional[float] = None
    extracted_text: Optional[str] = None
    upload_date: Optional[datetime] = None
    processed: int = 0

    class Config:
        from_attributes = True
