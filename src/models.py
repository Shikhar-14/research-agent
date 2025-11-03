from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Union
from datetime import datetime

class Quote(BaseModel):
    text: str
    speaker: Optional[str] = None
    context: Optional[str] = None
    url: HttpUrl

class NumberStat(BaseModel):
    metric: str
    value: Union[float, str]
    unit: Optional[str] = None
    year: Optional[int] = None
    url: HttpUrl

class Claim(BaseModel):
    statement: str
    polarity: Optional[str] = Field(default=None, description="pro/neutral/con")
    evidence_urls: List[HttpUrl]

class ExtractedDoc(BaseModel):
    url: HttpUrl
    domain: str
    title: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    language: Optional[str] = None
    entities: List[str] = []
    quotes: List[Quote] = []
    numbers: List[NumberStat] = []
    claims: List[Claim] = []
    summary: str
    raw_text_path: Optional[str] = ""
