from typing import List, Optional

from pydantic import Field, computed_field

from ...number_service.model import DocumentId
from ...util import EpoBaseModel, InpadocModel
from ..schema.biblio import BiblioResultSchema


class Citation(InpadocModel):
    cited_phase: Optional[str] = None
    cited_by: Optional[str] = None
    epodoc: Optional[DocumentId] = None
    docdb: Optional[DocumentId] = None
    original: Optional[DocumentId] = None

    def __repr__(self):
        return f"Citation(doc_number={str(self.docdb)}, cited_by={self.cited_by}, cited_phase={self.cited_phase})"

    @computed_field
    @property
    def docdb_number(self) -> str:
        num = self.docdb
        if num.kind:
            return f"{num.country}{num.number}.{num.kind}"
        return f"{num.country}{num.number}"


class Title(EpoBaseModel):
    lang: str
    text: str

    def __repr__(self) -> str:
        return f"Title(lang={self.lang}, text={self.text})"


def limit_text(string, limit=30):
    if len(string) < limit:
        return string
    else:
        return f"{string[:limit]}..."


class InpadocBiblio(InpadocModel):
    __manager__ = "...published.manager.BiblioManager"
    country: Optional[str] = None
    doc_number: Optional[str] = None
    kind: Optional[str] = None
    family_id: Optional[str] = None
    publication_number: Optional[str] = None
    application_number: Optional[str] = None
    publication_reference_docdb: Optional[DocumentId] = None
    publication_reference_epodoc: Optional[DocumentId] = None
    publication_reference_original: Optional[DocumentId] = None
    application_reference_docdb: Optional[DocumentId] = None
    application_reference_epodoc: Optional[DocumentId] = None
    application_reference_original: Optional[DocumentId] = None
    intl_class: List[str] = Field(default_factory=list)
    cpc_class: List[str] = Field(default_factory=list)
    us_class: List[str] = Field(default_factory=list)
    priority_claims: List[DocumentId] = Field(default_factory=list)
    title: Optional[str] = None
    titles: List[Title] = Field(default_factory=list)
    abstract: Optional[str] = None
    citations: List[Citation] = Field(default_factory=list)
    applicants_epodoc: List[str] = Field(default_factory=list)
    applicants_original: List[str] = Field(default_factory=list)
    inventors_epodoc: List[str] = Field(default_factory=list)
    inventors_original: List[str] = Field(default_factory=list)
    # TODO: NPL citations

    def __repr__(self):
        return f"InpadocBiblio(publication_number={self.publication_number}, title={limit_text(self.title, 30)})"


class BiblioResult(EpoBaseModel):
    __schema__ = BiblioResultSchema()
    documents: list[InpadocBiblio] = Field(default_factory=list)
