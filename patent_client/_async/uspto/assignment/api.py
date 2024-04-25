from pathlib import Path
from typing import TYPE_CHECKING, Optional

from yankee.base.schema import ListCollection

from patent_client._async.http_client import PatentClientSession

from .convert import convert_xml_to_json
from .model import AssignmentPage

if TYPE_CHECKING:
    from .model import Assignment

allowed_filters = [
    "PCTNumber",
    "OwnerName",
    "CorrespondentName",
    "PriorOwnerName",
    "ApplicationNumber",
    "PatentNumber",
    "PublicationNumber",
    "IntlRegistrationNumber",
    "ReelFrame",
]

allowed_sorts = ["ExecutionDate+desc", "ExecutionDate+asc"]


def validate_input(input, input_name, allowed_values):
    if input not in allowed_values:
        raise ValueError(f"{input_name} must be one of {allowed_values}")


client = PatentClientSession()


class AssignmentApi:
    @classmethod
    async def lookup(
        cls, query: str, filter: str, rows=8, start=0, sort="ExecutionDate+desc"
    ) -> ListCollection["Assignment"]:
        # Because of their limited utility, we omit fields, highlight, and facet
        url = "https://assignment-api.uspto.gov/patent/lookup"
        validate_input(filter, "filter", allowed_filters)
        validate_input(sort, "sort", allowed_sorts)
        response = await client.get(
            url,
            params={
                "filter": filter,
                "query": query,
                "rows": rows,
                "start": start,
                "sort": sort,
                "facet": "false",
            },
            headers={"Accept": "application/xml"},
        )
        response.raise_for_status()
        return AssignmentPage.model_validate(convert_xml_to_json(response.content))

    @classmethod
    async def download_pdf(
        cls, reel: str, frame: str, path: Optional[Path] = None
    ) -> Path:
        url = cls.get_download_url(reel, frame)

        if path is None:
            path = Path.cwd()
            output_path = output_path = path / f"assignment-pat-{reel}-{frame}.pdf"
        elif path.is_dir():
            output_path = path / f"assignment-pat-{reel}-{frame}.pdf"
        else:
            output_path = path

        with output_path.open("wb") as f:
            async with client.stream("GET", url) as response:
                async for chunk in response.aiter_bytes():
                    f.write(chunk)
        return output_path

    @classmethod
    def get_download_url(cls, reel: str, frame: str) -> str:
        url = f"https://assignment-api.uspto.gov/patent/download/{reel}/{frame}"
        return url
