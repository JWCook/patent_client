from typing import List, Optional

from pydantic import Field, computed_field

from ...util import EpoBaseModel, InpadocModel
from ..schema.search import SearchSchema


class Inpadoc(InpadocModel):
    family_id: Optional[str] = None
    id_type: Optional[str] = None
    country: Optional[str] = None
    doc_number: Optional[str] = None
    kind: Optional[str] = None

    @computed_field
    @property
    def docdb_number(self) -> str:
        return f"{self.country}{self.doc_number}{self.kind}"

    def download(self, path="."):
        return self.images.full_document.download(path)


class Search(EpoBaseModel):
    __schema__ = SearchSchema()
    query: Optional[str] = None
    num_results: Optional[int] = None
    begin: Optional[int] = None
    end: Optional[int] = None
    results: List[Inpadoc] = Field(default_factory=list)
