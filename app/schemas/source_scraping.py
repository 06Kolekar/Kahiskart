from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional


class ActionSchema(BaseModel):
    type: str  # search | click | input | select
    input_visible: Optional[bool]
    placeholder_text: Optional[str]
    value: Optional[str]
    enter_key: Optional[bool]


class ResultFieldSchema(BaseModel):
    label: str


class ResultMappingSchema(BaseModel):
    item_label: str
    fields: Dict[str, str]


class SourceScrapingCreate(BaseModel):
    source_id: int
    page_url: HttpUrl
    page_title: Optional[str]

    search_keyword: Optional[str]
    page_type: str

    actions: List[ActionSchema]
    results_mapping: Optional[ResultMappingSchema]


class SourceScrapingOut(SourceScrapingCreate):
    id: int

    class Config:
        orm_mode = True
