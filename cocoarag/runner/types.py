from __future__ import annotations
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field
import yaml


class TestEndPolicy(str, Enum):
    """
    TestingMode defines the different policies that can be considered
    to stop a session. By example, a session can end after a defined
    amount of questions or after the agent consumes a certain threshold
    even if the limit is not reached.
    """

    END_ON_LIMIT_REACHED = "END_ON_LIMIT_REACHED"
    END_ON_THRESHOLD_REACHED = "END_ON_THRESHOLD_REACHED"


class RunnerConfig(BaseModel):
    """Configurations for the testing session."""

    # Multithreading
    thread_count: int = Field(default=1, frozen=True)
    # Agents
    agents: dict[str, str]  # ex: {"llamma-31b-70b-instruct": "url/to/model"}
    # Policies
    test_end_policy: TestEndPolicy
    threshold: float = Field(default=0.51)
    max_iter: int | None = Field(frozen=True, default=100)
    # Runtime
    debug: bool = Field(default=False)

    @staticmethod
    def from_yaml(path: str) -> "RunnerConfig":
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            return RunnerConfig(**data)


class MetaData(BaseModel):
    """Represents the hyperparameters used in a test session."""

    ...


class Result(BaseModel):
    """Results represent a summary of an iteration of testing an agent"""

    score: float
    explored_territory: Decimal
    meta: MetaData
