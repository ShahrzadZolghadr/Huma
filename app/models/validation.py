from pydantic import BaseModel, Field


class ValidationIssue(BaseModel):
    code: str
    message: str


class ValidationResult(BaseModel):
    passed: bool
    issues: list[ValidationIssue] = Field(
        default_factory=list
    )