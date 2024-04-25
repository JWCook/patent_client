from typing import List, Optional

from pydantic import Field

from ..number_service.model import DocumentId
from ..util import EpoBaseModel
from .schema import FamilySchema


class PriorityClaim(EpoBaseModel):
    application_number: Optional[str] = None
    application_reference: Optional[DocumentId] = None
    sequence: Optional[int] = None
    kind: Optional[str] = None
    active: Optional[bool] = None


class FamilyMember(EpoBaseModel):
    publication_number: Optional[str] = None
    application_number: Optional[str] = None
    family_id: Optional[str] = None
    publication_reference: list = Field(default_factory=list)
    application_reference: list = Field(default_factory=list)
    priority_claims: List[PriorityClaim] = Field(default_factory=list)

    @property
    def docdb_number(self):
        return self.publication_number


class Family(EpoBaseModel):
    __schema__ = FamilySchema()
    publication_reference: Optional[DocumentId] = None
    num_records: Optional[int] = None
    publication_number: Optional[str] = None
    family_members: List[FamilyMember] = Field(default_factory=list)
