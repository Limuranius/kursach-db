from .models import Database
from .model_objects import UserStatus
from django.core.exceptions import ValidationError


class UserManager:

    @classmethod
    def get_status(cls, login: str, password: str) -> UserStatus:
        employee = Database.Employee.get(login)
        if employee is not None and employee.password == password:
            return UserStatus(employee.job_title)

        customer_user = Database.CustomerUser.get(login)
        if customer_user is not None and customer_user.password == password:
            return UserStatus.CUSTOMER

        raise ValidationError("Логин или пароль введены неправильно")
