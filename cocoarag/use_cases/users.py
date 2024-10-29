# use_cases.py
from cocoarag.models.users import UserModel
from cocoarag.services.users import AddUserService


class AddUserUseCase:
    def __call__(self,
                 user: UserModel) -> None:
        service = AddUserService()
        service(user=user)
