from django import forms
from .model_objects import UserStatus
from .models import Database, BaseDBModel


class BaseCreateForm(forms.Form):
    model: BaseDBModel

    def save_to_db(self):
        fields = dict()
        for field_name in self.fields:
            fields[field_name] = self.cleaned_data[field_name]
        data = self.__convert_data(fields)
        self.model.create(*data)

    def __convert_data(self, fields: dict) -> tuple:
        return tuple(fields.values())


class ProviderCreateForm(BaseCreateForm):
    model = Database.Provider
    name = forms.CharField(label="Название поставщика", max_length=50)
    address = forms.CharField(label="Адрес поставщика", max_length=100)


class FlowerCreateForm(BaseCreateForm):
    model = Database.Flower
    name = forms.CharField(label="Название", max_length=50)
    price = forms.IntegerField(label="Цена за рассаду")
    provider_name = forms.ChoiceField(label="Поставщик")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_providers(Database.Provider.all_names())

    def set_providers(self, provider_names: list[str]):
        choices = [(name, name) for name in provider_names]
        self.fields["provider_name"].choices = choices

    def __convert_data(self, fields: dict) -> tuple:
        provider_id = Database.Provider.get_provider_id(fields["provider_name"])
        return fields["name"], fields["price"], provider_id


class CustomerCreateForm(BaseCreateForm):
    model = Database.Customer
    name = forms.CharField(label="Название заказчика", max_length=50)
    phone = forms.CharField(label="Телефон заказчика", max_length=50)
    address = forms.CharField(label="Адрес заказчика", max_length=100)


class ContractCreateForm(BaseCreateForm):
    model = Database.Contract
    customer_name = forms.ChoiceField(label="Заказчик")
    register_date = forms.DateField(label="Дата регистрации", widget=forms.DateInput({"type": "date"}))
    execution_date = forms.DateField(label="Дата исполнения", widget=forms.DateInput({"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_customers(Database.Customer.all_names())

    def set_customers(self, customer_names: list[str]):
        choices = [(name, name) for name in customer_names]
        self.fields["customer_name"].choices = choices

    def __convert_data(self, fields: dict) -> tuple:
        customer_id = Database.Customer.get_customer_id(fields["customer_name"])
        return fields["customer_name"], fields["register_date"], fields["execution_date"], customer_id


class OrderCreateForm(BaseCreateForm):
    model = Database.Order
    contract_id = forms.ChoiceField(label="Номер договора")
    flower_name = forms.ChoiceField(label="Название цветка")
    quantity = forms.IntegerField(label="Количество рассады")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_contracts(Database.Contract.all_ids())
        self.set_flowers(Database.Flower.all_names())

    def set_contracts(self, contract_ids: list[int]):
        choices = [(contract_id, contract_id) for contract_id in contract_ids]
        self.fields["contract_id"].choices = choices

    def set_flowers(self, flower_names: list[str]):
        choices = [(name, name) for name in flower_names]
        self.fields["flower_name"].choices = choices

    def __convert_data(self, fields: dict) -> tuple:
        flower_id = Database.Flower.get_flower_id(fields["flower_name"])
        return fields["contract_id"], flower_id, fields["quantity"]


class EmployeeRegisterForm(BaseCreateForm):
    model = Database.Employee
    login = forms.CharField(label="Логин", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    job_title = forms.ChoiceField(label="Должность", choices=((e.value, e.value) for e in UserStatus))


class CustomerRegisterForm(BaseCreateForm):
    login = forms.CharField(label="Логин", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    name = forms.CharField(label="Название компании", max_length=50)


class LoginForm(forms.Form):
    login = forms.CharField(label="Логин", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
