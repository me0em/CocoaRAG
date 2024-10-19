# models/filters.py
from pydantic import BaseModel, Field, field_validator
from typing import Any

class FilterCondition(BaseModel):
    """Defines a condition for filtering"""
    field: str  # e.g., 'id', 'location'
    operator: str  # e.g., '$in', '$eq', '$like'
    value: Any  # Could be a list, number, or string based on the operator


class FilterModel(BaseModel):
    """ Represents a complex filter for similarity search
    """
    # This Model expect filter to be using operators ($AND, $IN) only!!!!!
    content: dict[str, dict[str, list[str]]] | dict = Field(description="Filter logic for the query")

    # @field_validator("content")
    # def validate_filter(val):
    #     valid_operators = ['$in', '$nin']
    #     # valid_columns = []

    #     # def check_operator(d):
    #     #     for key, val in d.items():
    #     #         if key not in valid_operators:
    #     #             raise ValueError(f"Invalid operator '{key}' in filter. Supported operators are: {valid_operators}")
    #     #         if isinstance(val, dict):
    #     #             check_operator(val)
    #     #         if isinstance(val, list):
    #     #             for v in val:
    #     #                 if isinstance(v, dict):
    #     #                     check_operator(v)
        
    #     # # Validate operators
    #     # check_operator(val)
    #     return val

