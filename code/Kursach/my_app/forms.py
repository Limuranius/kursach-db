from django import forms
from .model_objects import UserStatus, BaseModelObj
from .models import Database, BaseDBModel


class BaseCreateForm(forms.Form):
    model: BaseDBModel

    def save_to_db(self):
        fields = dict()
        for field_name in self.fields:
            fields[field_name] = self.cleaned_data[field_name]
        data = self._convert_data(fields)
        self.model.create(*data)

    def _convert_data(self, fields: dict) -> tuple:
        return tuple(fields.values())


class BaseUpdateForm(forms.Form):
    model: BaseDBModel

    primary_params: dict
    obj: BaseModelObj

    def __init__(self, primary_params, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.primary_params = primary_params
        self.obj = self.model.get(*primary_params.values())
        self.fill_fields()

    def save_to_db(self):
        fields = dict()
        for field_name in self.fields:
            fields[field_name] = self.cleaned_data[field_name]
        new_params = self._convert_data(fields)
        self.obj.update(*new_params)

    def _convert_data(self, fields: dict) -> tuple:
        return tuple(fields.values())

    def fill_fields(self):
        for field in self.fields:
            self.fields[field].initial = getattr(self.obj, field)


class ProviderForm(forms.Form):
    model = Database.Provider
    name = forms.CharField(label="Название поставщика", max_length=50)
    address = forms.CharField(label="Адрес поставщика", max_length=100)


class ProviderCreateForm(ProviderForm, BaseCreateForm):
    pass


class ProviderUpdateForm(ProviderForm, BaseUpdateForm):
    pass


class FlowerForm(forms.Form):
    model = Database.Flower
    name = forms.CharField(label="Название", max_length=50)
    price = forms.IntegerField(label="Цена за рассаду")
    provider_name = forms.ChoiceField(label="Поставщик")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_providers(Database.Provider.all_names())

    def _set_providers(self, provider_names: list[str]):
        choices = [(name, name) for name in provider_names]
        self.fields["provider_name"].choices = choices

    def _convert_data(self, fields: dict) -> tuple:
        provider_id = Database.Provider.get_provider_id(fields["provider_name"])
        return fields["name"], fields["price"], provider_id


class FlowerCreateForm(FlowerForm, BaseCreateForm):
    pass


class FlowerUpdateForm(FlowerForm, BaseUpdateForm):
    pass


class CustomerForm(forms.Form):
    model = Database.Customer
    name = forms.CharField(label="Название заказчика", max_length=50)
    phone = forms.CharField(label="Телефон заказчика", max_length=50)
    address = forms.CharField(label="Адрес заказчика", max_length=100)


class CustomerCreateForm(CustomerForm, BaseCreateForm):
    pass


class CustomerUpdateForm(CustomerForm, BaseUpdateForm):
    pass


class ContractForm(forms.Form):
    model = Database.Contract
    customer_name = forms.ChoiceField(label="Заказчик")
    register_date = forms.DateField(label="Дата регистрации", widget=forms.DateInput({"type": "date"}))
    execution_date = forms.DateField(label="Дата исполнения", widget=forms.DateInput({"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_customers(Database.Customer.all_names())

    def _set_customers(self, customer_names: list[str]):
        choices = [(name, name) for name in customer_names]
        self.fields["customer_name"].choices = choices

    def _convert_data(self, fields: dict) -> tuple:
        customer_id = Database.Customer.get_customer_id(fields["customer_name"])
        return fields["customer_name"], fields["register_date"], fields["execution_date"], customer_id


class ContractCreateForm(ContractForm, BaseCreateForm):
    pass


class ContractUpdateForm(ContractForm, BaseUpdateForm):
    pass


class OrderForm(forms.Form):
    model = Database.Order
    contract_id = forms.ChoiceField(label="Номер договора")
    flower_name = forms.ChoiceField(label="Название цветка")
    quantity = forms.IntegerField(label="Количество рассады")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_contracts(Database.Contract.all_ids())
        self._set_flowers(Database.Flower.all_names())

    def _set_contracts(self, contract_ids: list[int]):
        choices = [(contract_id, contract_id) for contract_id in contract_ids]
        self.fields["contract_id"].choices = choices

    def _set_flowers(self, flower_names: list[str]):
        choices = [(name, name) for name in flower_names]
        self.fields["flower_name"].choices = choices

    def _convert_data(self, fields: dict) -> tuple:
        flower_id = Database.Flower.get_flower_id(fields["flower_name"])
        return fields["contract_id"], flower_id, fields["quantity"]


class OrderCreateForm(OrderForm, BaseCreateForm):
    pass


class OrderUpdateForm(OrderForm, BaseUpdateForm):
    pass


class EmployeeForm(forms.Form):
    model = Database.Employee
    login = forms.CharField(label="Логин", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    job_title = forms.ChoiceField(label="Должность", choices=((e.value, e.value) for e in UserStatus))


class EmployeeRegisterForm(EmployeeForm, BaseCreateForm):
    pass


class EmployeeUpdateForm(EmployeeForm, BaseUpdateForm):
    pass


class CustomerForm(forms.Form):
    model = Database.CustomerUser
    login = forms.CharField(label="Логин", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    name = forms.CharField(label="Название компании", max_length=50)


class CustomerUserRegisterForm(CustomerForm, BaseCreateForm):
    pass


class CustomerUserUpdateForm(CustomerForm, BaseUpdateForm):
    pass


class LoginForm(forms.Form):
    login = forms.CharField(label="Логин", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())
