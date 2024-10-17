# models/filters.py
from pydantic import BaseModel, Field, root_validator
from typing import Any, Dict, List, Union

class FilterCondition(BaseModel):
    """Defines a condition for filtering"""
    field: str  # e.g., 'id', 'location'
    operator: str  # e.g., '$in', '$eq', '$like'
    value: Any  # Could be a list, number, or string based on the operator


class FilterModel(BaseModel):
    """Represents a complex filter for similarity search"""
    filter: Dict[str, Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(description="Filter logic for the query")

    @root_validator
    def validate_filter(cls, values):
        filter_logic = values.get('filter')
        valid_operators = ['$eq', '$ne', '$lt', '$lte', '$gt', '$gte', '$in', '$nin', '$between', '$like', '$ilike', '$and', '$or']

        def check_operator(d):
            for key, val in d.items():
                if key not in valid_operators:
                    raise ValueError(f"Invalid operator '{key}' in filter. Supported operators are: {valid_operators}")
                if isinstance(val, dict):
                    check_operator(val)
                if isinstance(val, list):
                    for v in val:
                        if isinstance(v, dict):
                            check_operator(v)
        
        # Validate operators
        check_operator(filter_logic)
        return values

