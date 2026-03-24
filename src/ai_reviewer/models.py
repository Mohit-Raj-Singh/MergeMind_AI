from enum import StrEnum
from pydantic import BaseModel, Field


class Severity(StrEnum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SECURITY = "security"


class InlineComment(BaseModel):
    path: str = Field(description="File path relative to repo root")
    line: int = Field(description="Line number in the NEW file")
    severity: Severity
    title: str = Field(description="Short one-line title")
    body: str = Field(description="Detailed explanation and suggested fix")


class ReviewSummary(BaseModel):
    overall: str = Field(description="One paragraph overall assessment")
    highlights: list[str] = Field(description="Up to 5 positive things")
    issues: list[str] = Field(description="Top issues across the whole diff")
    security_flags: list[str] = Field(description="Any security concerns")


class ReviewResult(BaseModel):
    summary: ReviewSummary
    inline_comments: list[InlineComment]
