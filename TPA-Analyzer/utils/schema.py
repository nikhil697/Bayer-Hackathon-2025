from pydantic import BaseModel, Field
from typing import Optional

class TPAMetadata(BaseModel):
    vendor_name: Optional[str] = Field(None, description="Vendor or TPA name")
    contract_start_date: Optional[str] = Field(None, description="Contract Start Date")
    contract_end_date: Optional[str]
    payment_terms: Optional[str]
    scope_of_services: Optional[str]
    sla_clause: Optional[str]
    penalty_clause: Optional[str]
    termination_clause: Optional[str]
    renewal_type: Optional[str]
    confidentiality_clause: Optional[str]