from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator

MAX_SERVICES = 200
MAX_DEPENDENCIES = 1000
MAX_TEAMS = 100
MAX_TEXT_LENGTH = 4000
MAX_ID_LENGTH = 100
MAX_NAME_LENGTH = 200


class Service(BaseModel):
    id: str = Field(min_length=1, max_length=MAX_ID_LENGTH)
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    owner_team: str = Field(min_length=1, max_length=MAX_ID_LENGTH)
    criticality: Literal["critical", "high", "medium", "low"]
    description: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class Dependency(BaseModel):
    from_service: str = Field(min_length=1, max_length=MAX_ID_LENGTH)
    to_service: str = Field(min_length=1, max_length=MAX_ID_LENGTH)
    dependency_type: Literal["sync-api", "async-event", "database", "shared-library"]
    strength: Literal["hard", "soft"]


class Team(BaseModel):
    id: str = Field(min_length=1, max_length=MAX_ID_LENGTH)
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    owns: List[str] = Field(default_factory=list, max_length=MAX_SERVICES)
    size: int
    focus: Literal["platform", "product", "data", "security", "other"]


class Decision(BaseModel):
    title: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    description: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)
    decision_type: Literal[
        "architecture",
        "migration",
        "deprecation",
        "reorg",
        "vendor",
        "api-change",
        "infrastructure",
    ]
    affected_services: List[str] = Field(default_factory=list, max_length=MAX_SERVICES)
    timeline: Literal["immediate", "weeks", "months", "quarters"]
    reversibility: Literal["easy", "moderate", "hard", "irreversible"]


class BlastRadiusRequest(BaseModel):
    services: List[Service] = Field(default_factory=list, max_length=MAX_SERVICES)
    dependencies: List[Dependency] = Field(
        default_factory=list, max_length=MAX_DEPENDENCIES
    )
    teams: List[Team] = Field(default_factory=list, max_length=MAX_TEAMS)
    decision: Decision
    additional_context: Optional[str] = Field(default=None, max_length=MAX_TEXT_LENGTH)

    @model_validator(mode="after")
    def validate_relationships(self):
        service_ids = {service.id for service in self.services}

        if len(service_ids) != len(self.services):
            raise ValueError("Service ids must be unique.")

        for dependency in self.dependencies:
            if (
                dependency.from_service not in service_ids
                or dependency.to_service not in service_ids
            ):
                raise ValueError("Dependencies must reference declared services.")

        for team in self.teams:
            if any(service_id not in service_ids for service_id in team.owns):
                raise ValueError("Teams must only own declared services.")

        for affected_service in self.decision.affected_services:
            if affected_service not in service_ids:
                raise ValueError("Affected services must reference declared services.")

        return self
