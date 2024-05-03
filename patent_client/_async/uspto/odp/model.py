import datetime
from enum import Enum
from typing import Any, List, Optional

from async_property import async_property
from async_property.base import AsyncPropertyDescriptor
from pydantic import AliasPath, BeforeValidator, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel
from typing_extensions import Annotated

from patent_client.util.pydantic_util import BaseModel


class BaseODPModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, ignored_types=(AsyncPropertyDescriptor,))


# Common


class Address(BaseODPModel):
    city_name: Optional[str] = Field(alias="cityName", default=None)
    geographic_region_name: Optional[str] = Field(alias="geographicRegionName", default=None)
    geographic_region_code: Optional[str] = Field(alias="geographicRegionCode", default=None)
    country_code: Optional[str] = Field(alias="countryCode", default=None)
    postal_code: Optional[str] = Field(alias="postalCode", default=None)
    country_name: Optional[str] = Field(alias="countryName", default=None)
    address_line_one_text: Optional[str] = Field(alias="addressLineOneText", default=None)
    address_line_two_text: Optional[str] = Field(alias="addressLineTwoText", default=None)
    name_line_one_text: Optional[str] = Field(alias="nameLineOneText", default=None)
    name_line_two_text: Optional[str] = Field(alias="nameLineTwoText", default=None)
    postal_address_category: Optional[str] = Field(alias="postalAddressCategory", default=None)
    correspondent_name_text: Optional[str] = Field(alias="correspondentNameText", default=None)


# Continuity


class Relationship(BaseODPModel):
    application_status_code: Optional[int] = Field(default=None)
    claim_type_code: Optional[str] = Field(alias="claimParentageTypeCode", default=None)
    filing_date: Optional[datetime.date] = Field(default=None)
    application_status_description: Optional[str] = Field(
        alias="applicationStatusDescriptionText", default=None
    )
    claim_type_description: Optional[str] = Field(
        alias="claimParentageTypeCodeDescription", default=None
    )
    parent_application_id: Optional[str] = Field(alias="parentApplicationNumberText", default=None)
    child_application_id: Optional[str] = Field(alias="childApplicationNumberText", default=None)


class Continuity(BaseODPModel):
    count: Optional[int] = Field(default=None)
    request_identifier: Optional[str] = Field(default=None)
    parent_continuity: Optional[list[Relationship]] = Field(
        alias=AliasPath(["patentBag", 0, "continuityBag", "parentContinuityBag"]),
        default_factory=list,
    )
    child_continuity: Optional[list[Relationship]] = Field(
        alias=AliasPath(["patentBag", 0, "continuityBag", "childContinuityBag"]),
        default_factory=list,
    )


# Documents


class DownloadOption(BaseODPModel):
    mime_type_identifier: Optional[str] = Field(default=None)
    download_url: Optional[str] = Field(default=None)
    pages: Optional[int] = Field(alias="pageTotalQuantity", default=None)


class Document(BaseODPModel):
    appl_id: Optional[str] = Field(alias="applicationNumberText", default=None)
    mail_date: Optional[datetime.datetime] = Field(alias="officialDate", default=None)
    document_identifier: Optional[str] = Field(alias="documentIdentifier", default=None)
    document_code: Optional[str] = Field(alias="documentCode", default=None)
    document_code_description: Optional[str] = Field(
        alias="documentCodeDescriptionText", default=None
    )
    direction_category: Optional[str] = Field(alias="directionCategory", default=None)
    download_option_bag: list[dict] = Field(alias="downloadOptionBag", default_factory=list)

    async def download(self, type="PDF", out_path=None):
        from .manager import api

        try:
            url = next(u for u in self.download_option_bag if u["mimeTypeIdentifier"] == type)[
                "downloadUrl"
            ]
        except StopIteration:
            raise ValueError(f"No download URL found for this document type: {type}")
        if out_path is None:
            out_path = f"{self.appl_id} - {self.mail_date.date()} - {self.document_code} - {self.document_code_description}.{type.lower()}".replace(
                "/", "-"
            )
        return await api.client.download(url, "GET", path=out_path)


# Assignment


class Assignor(BaseODPModel):
    execution_date: Optional[datetime.date] = Field(alias="executionDate", default=None)
    assignor_name: Optional[str] = Field(alias="assignorName", default=None)


class AssigneeAddress(BaseODPModel):
    city_name: Optional[str] = Field(alias="cityName", default=None)
    geographic_region_code: Optional[str] = Field(alias="geographicRegionCode", default=None)
    postal_code: Optional[str] = Field(alias="postalCode", default=None)
    address_line_one_text: Optional[str] = Field(alias="addressLineOneText", default=None)


class Assignee(BaseODPModel):
    assignee_address: Optional[AssigneeAddress] = Field(alias="assigneeAddress", default=None)
    assignee_name_text: Optional[str] = Field(alias="assigneeNameText", default=None)


class Assignment(BaseODPModel):
    assignment_received_date: Optional[datetime.date] = Field(
        alias="assignmentReceivedDate", default=None
    )
    frame_number: Optional[str] = Field(alias="frameNumber", default=None)
    page_number: Optional[int] = Field(alias="pageNumber", default=None)
    reel_number_frame_number: Optional[str] = Field(alias="reelNumber/frameNumber", default=None)
    assignment_recorded_date: Optional[datetime.date] = Field(
        alias="assignmentRecordedDate", default=None
    )
    conveyance_text: Optional[str] = Field(alias="conveyanceText", default=None)
    assignment_mailed_date: Optional[datetime.date] = Field(
        alias="assignmentMailedDate", default=None
    )
    reel_number: Optional[str] = Field(alias="reelNumber", default=None)
    assignor_bag: list[Assignor] = Field(alias="assignorBag", default_factory=list)
    assignee_bag: list[Assignee] = Field(alias="assigneeBag", default_factory=list)
    correspondence_address: list[Address] = Field(
        alias="correspondenceAddress", default_factory=list
    )


# Foreign Priority


class ForeignPriority(BaseODPModel):
    priority_number_text: Optional[str] = Field(alias="priorityNumberText", default=None)
    filing_date: Optional[datetime.date] = Field(alias="filingDate", default=None)
    country_name: Optional[str] = Field(alias="countryName", default=None)


# Attorney


class TelecommunicationAddress(BaseODPModel):
    telecommunication_number: Optional[str] = Field(alias="telecommunicationNumber", default=None)
    usage_type_category: Optional[str] = Field(alias="usageTypeCategory", default=None)


class Attorney(BaseODPModel):
    active_indicator: Optional[str] = Field(alias="activeIndicator", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    registration_number: Optional[str] = Field(alias="registrationNumber", default=None)
    attorney_address_bag: list[Address] = Field(alias="attorneyAddressBag", default_factory=list)
    telecommunication_address_bag: list[TelecommunicationAddress] = Field(
        alias="telecommunicationAddressBag", default_factory=list
    )
    registered_practitioner_category: Optional[str] = Field(
        alias="registeredPractitionerCategory", default=None
    )
    name_suffix: Optional[str] = Field(alias="nameSuffix", default=None)


class CustomerNumber(BaseODPModel):
    attorneys: list[Attorney] = Field(alias="attorneyBag", default_factory=list)
    customer_number: Optional[str] = Field(
        alias=AliasPath("customerNumber", "patronIdentifier"), default=None
    )
    address: Optional[Address] = Field(
        alias=AliasPath("customerNumber", "powerOfAttorneyAddressBag", 0), default=None
    )


# Transactions


class Transaction(BaseODPModel):
    recorded_date: Optional[datetime.date] = Field(alias="recordedDate", default=None)
    transaction_code: Optional[str] = Field(alias="caseActionCode", default=None)
    transaction_description: Optional[str] = Field(alias="caseActionDescriptionText", default=None)


# Adjustment Data
class TermAdjustmentHistory(BaseODPModel):
    applicant_day_delay_quantity: Optional[int] = Field(
        alias="applicantDayDelayQuantity", default=None
    )
    start_sequence_number: Optional[float] = Field(alias="startSequenceNumber", default=None)
    case_action_description_text: Optional[str] = Field(
        alias="caseActionDescriptionText", default=None
    )
    case_action_sequence_number: Optional[float] = Field(
        alias="caseActionSequenceNumber", default=None
    )
    action_date: Optional[datetime.date] = Field(alias="actionDate", default=None)


class TermAdjustment(BaseODPModel):
    applicant_day_delay_quantity: Optional[int] = Field(
        alias="applicantDayDelayQuantity", default=None
    )
    overlapping_day_quantity: Optional[int] = Field(alias="overlappingDayQuantity", default=None)
    filing_date: Optional[datetime.date] = Field(alias="filingDate", default=None)
    c_delay_quantity: Optional[int] = Field(alias="cDelayQuantity", default=None)
    adjustment_total_quantity: Optional[int] = Field(alias="adjustmentTotalQuantity", default=None)
    b_delay_quantity: Optional[int] = Field(alias="bDelayQuantity", default=None)
    grant_date: Optional[datetime.date] = Field(alias="grantDate", default=None)
    a_delay_quantity: Optional[int] = Field(alias="aDelayQuantity", default=None)
    non_overlapping_day_quantity: Optional[int] = Field(
        alias="nonOverlappingDayQuantity", default=None
    )
    ip_office_day_delay_quantity: Optional[int] = Field(
        alias="ipOfficeDayDelayQuantity", default=None
    )
    history: Optional[list[TermAdjustmentHistory]] = Field(
        alias="patentTermAdjustmentHistoryDataBag", default_factory=list
    )


# Application Object

YNBool = Annotated[bool, BeforeValidator(lambda v: v == "Y")]


class Inventor(BaseODPModel):
    first_name: Optional[str] = Field(alias="firstName", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    full_name: Optional[str] = Field(alias="inventorNameText", default=None)
    addresses: list[Address] = Field(alias="correspondenceAddressBag", default_factory=list)


class Applicant(BaseODPModel):
    applicant_name: Optional[str] = Field(alias="applicantNameText", default=None)
    addresses: list[Address] = Field(alias="correspondenceAddressBag", default_factory=list)
    app_status_code: Optional[int] = Field(alias="applicationStatusCode", default=None)
    app_status: Optional[str] = Field(alias="applicationStatusDescriptionText", default=None)


class USApplicationBiblio(BaseODPModel):
    aia_indicator: Optional[YNBool] = Field(alias="firstInventorToFileIndicator", default=None)
    app_filing_date: Optional[datetime.date] = Field(alias="filingDate", default=None)
    inventors: list[Inventor] = Field(alias="inventorBag", default_factory=list)
    customer_number: Optional[int] = Field(alias="customerNumber", default=None)
    group_art_unit: Optional[str] = Field(alias="groupArtUnitNumber", default=None)
    invention_title: Optional[str] = Field(alias="inventionTitle", default=None)
    correspondence_address: list[Address] = Field(
        alias="correspondenceAddressBag", default_factory=list
    )
    app_conf_num: Optional[int] = Field(alias="applicationConfirmationNumber", default=None)
    atty_docket_num: Optional[str] = Field(alias="docketNumber", default=None)
    appl_id: Optional[str] = Field(alias="applicationNumberText", default=None)
    first_inventor_name: Optional[str] = Field(alias="firstInventorName", default=None)
    first_applicant_name: Optional[str] = Field(alias="firstApplicantName", default=None)
    cpc_classifications: list[str] = Field(alias="cpcClassificationBag", default_factory=list)
    entity_status: Optional[str] = Field(alias="businessEntityStatusCategory", default=None)
    app_early_pub_number: Optional[str] = Field(alias="earliestPublicationNumber", default=None)

    @async_property
    async def bibliographic_data(self) -> "USApplicationBiblio":
        return await self._get_model(".model.USApplicationBiblio").objects.get(appl_id=self.appl_id)

    @async_property
    async def application(self) -> "USApplication":
        return await self._get_model(".model.USApplication").objects.get(appl_id=self.appl_id)

    @async_property
    async def continuity(self) -> Continuity:
        return await self._get_model(".model.Continuity").objects.get(appl_id=self.appl_id)

    @async_property
    async def documents(self) -> list[Document]:
        return self._get_model(".model.Document").objects.filter(appl_id=self.appl_id)

    @async_property
    async def term_adjustment(self) -> TermAdjustment:
        return self._get_model(".model.TermAdjustment").objects.filter(appl_id=self.appl_id)

    @async_property
    async def assignments(self) -> list[Assignment]:
        return self._get_model(".model.Assignment").objects.filter(appl_id=self.appl_id)

    @async_property
    async def customer_number(self) -> CustomerNumber:
        return self._get_model(".model.CustomerNumber").objects.filter(appl_id=self.appl_id)

    @async_property
    async def foreign_priority(self) -> ForeignPriority:
        return self._get_model(".model.ForeignPriority").objects.filter(appl_id=self.appl_id)

    @async_property
    async def transactions(self) -> list[Transaction]:
        return self._get_model(".model.Transaction").objects.filter(appl_id=self.appl_id)

    # Aliases

    @async_property
    async def biblio(self) -> "USApplicationBiblio":
        return await self.bibliographic_data

    @async_property
    async def app(self) -> "USApplication":
        return await self.application

    @async_property
    async def docs(self) -> list[Document]:
        return await self.documents


class USApplication(BaseODPModel):
    aia_indicator: Optional[YNBool] = Field(alias="firstInventorToFileIndicator", default=None)
    app_filing_date: Optional[datetime.date] = Field(alias="filingDate", default=None)
    inventors: list[Inventor] = Field(alias="inventorBag", default_factory=list)
    customer_number: Optional[int] = Field(alias="customerNumber", default=None)
    group_art_unit: Optional[str] = Field(alias="groupArtUnitNumber", default=None)
    invention_title: Optional[str] = Field(alias="inventionTitle", default=None)
    correspondence_address: list[Address] = Field(
        alias="correspondenceAddressBag", default_factory=list
    )
    app_conf_num: Optional[int] = Field(alias="applicationConfirmationNumber", default=None)
    atty_docket_num: Optional[str] = Field(alias="docketNumber", default=None)
    appl_id: Optional[str] = Field(alias="applicationNumberText", default=None)
    first_inventor_name: Optional[str] = Field(alias="firstInventorName", default=None)
    first_applicant_name: Optional[str] = Field(alias="firstApplicantName", default=None)
    cpc_classifications: list[str] = Field(alias="cpcClassificationBag", default_factory=list)
    entity_status: Optional[str] = Field(alias="businessEntityStatusCategory", default=None)
    app_early_pub_number: Optional[str] = Field(alias="earliestPublicationNumber", default=None)

    app_type_code: Optional[str] = Field(alias="applicationTypeCode", default=None)
    national_stage_indicator: Optional[YNBool] = Field(alias="nationalStageIndicator", default=None)

    effective_filing_date: Optional[datetime.date] = Field(
        alias="effectiveFilingDate", default=None
    )
    cls_sub_cls: Optional[str] = Field(alias="class/subclass", default=None)
    assignments: list[Assignment] = Field(alias="assignmentBag", default_factory=list)
    attorneys: Optional[CustomerNumber] = Field(alias="recordAttorney", default=None)
    transactions: list[Transaction] = Field(alias="transactionContentBag", default_factory=list)
    parent_applications: Optional[list[Relationship]] = Field(
        alias=AliasPath("continuityBag", "parentContinuityBag"), default_factory=list
    )
    child_applications: Optional[list[Relationship]] = Field(
        alias=AliasPath("continuityBag", "childContinuityBag"), default_factory=list
    )
    patent_term_adjustment: Optional[TermAdjustment] = Field(
        alias="patentTermAdjustmentData", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def _validate_patent_term_adjustment(cls, v):
        if "patentTermAdjustmentData" in v and v["patentTermAdjustmentData"] == dict():
            v["patentTermAdjustmentData"] = None
        return v


## RESPONSE Models


class SearchResult(BaseODPModel):
    filing_date: Optional[datetime.date] = Field(default=None)
    appl_id: Optional[str] = Field(alias="applicationNumberText", default=None)
    invention_title: Optional[str] = Field(alias="inventionTitle", default=None)
    filing_date: Optional[datetime.date] = Field(default=None)
    patent_number: Optional[str] = Field(alias="patentNumber", default=None)


class SearchResponse(BaseODPModel):
    count: Optional[int] = Field(default=None)
    results: list[SearchResult] = Field(alias="patentBag", default_factory=list)
    request_id: Optional[str] = Field(alias="requestIdentifier", default=None)


## Request Models


class Filter(BaseModel):
    name: Optional[str] = Field(default=None)
    value: Optional[List[str]] = Field(default_factory=list)


class Range(BaseModel):
    field: Optional[str] = Field(examples=["grantDate"], default=None)
    valueFrom: Optional[str] = Field(examples=["2020-01-01"], default=None)
    valueTo: Optional[str] = Field(examples=["2020-12-31"], default=None)

    @model_validator(mode="before")
    @classmethod
    def add_default_dates(cls, data: Any) -> Any:
        if data.get("valueFrom") is None:
            data["valueFrom"] = "1776-07-04"
        if data.get("valueTo") is None:
            data["valueTo"] = datetime.date.today().isoformat()
        return data


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
    Asc = "Asc"
    Desc = "Desc"


class Sort(BaseModel):
    field: Optional[str] = Field(examples=["grantDate"], default=None)
    order: Optional[SortOrder] = Field(examples=[SortOrder.desc], default=None)


class Pagination(BaseModel):
    offset: Optional[int] = Field(examples=[0], default=0, ge=0)
    limit: Optional[int] = Field(examples=[25], default=25, ge=1)


class SearchRequest(BaseModel):
    q: Optional[str] = Field(default="")
    filters: Optional[List[Filter]] = Field(default_factory=list)
    rangeFilters: Optional[List[Range]] = Field(default_factory=list)
    sort: Optional[List[Sort]] = Field(default_factory=list)
    fields: Optional[List[str]] = Field(default_factory=list)
    pagination: Optional[Pagination] = Field(default=None)
    facets: Optional[List[str]] = Field(default_factory=list)


class SearchGetRequest(BaseModel):
    q: Optional[str] = Field(default="")
    sort: Optional[str] = Field(default="filingDate")
    fields: Optional[str] = Field(default="")
    offset: Optional[int] = Field(default=0)
    limit: Optional[int] = Field(default=25)
