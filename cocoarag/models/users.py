from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class UserModel(BaseModel):
    """ A model representing a user
    """
    user_id: UUID = Field(default_factory=uuid4,
                          frozen=True,
                          description="UUID represents a single user")
    user_group: UUID = Field(description="UUID represents a user's group")
    username: str = Field(description="Username")
    email: str = Field(description="Email address of the user")
    password_hash: str = Field(description="Hashed password of the user")
    metadata: dict = Field(default_factory=dict,
                           description="Additional metadata about the user")
