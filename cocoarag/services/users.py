from cocoarag.dao.users import AddUserDAO
from cocoarag.models.users import UserModel


class AddUserService:
    """ User sign up
    """
    def __call__(self,
                 user: UserModel) -> None:
        accessor = AddUserDAO()
        accessor(
            user.user_id,
            user.user_group,
            user.username,
            user.email,
            user.password_hash,
            user.metadata
        )
