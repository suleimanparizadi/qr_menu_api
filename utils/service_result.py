from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class ServiceResult(Generic[T]):

    success: bool
    message: str = ""
    data: T | None = None
    code: str | None = None



    @classmethod
    def success(cls,  message="", data=None):
        return cls(
            success=True,
            message=message,
            data=data
        )


    @classmethod
    def fail(cls ,message, code=None):
        return cls(
            success=False,
            message=message,
            code=code
        )




# Example: ServiceResult[User]
# This result contains a User.

# Example: ServiceResult[Cart]
# # This result contains a Cart. (an object type)



#class ServiceResult:

#    def __init__(self, success, message="", data=None):
#        self.success = success
#        self.message = message
#       self.data = data
