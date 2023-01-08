from django.shortcuts import render, redirect
from .models import Database, BaseDBModel
from django.views import View
from . import forms
from .mixins import UserStatusRequiredMixin
from .user_manager import UserManager
from .model_objects import UserStatus
from django.core.exceptions import ValidationError


class IndexView(View):
    def get(self, request):
        return render(request, "my_app/index.html")


class BaseTableView(UserStatusRequiredMixin, View):
    model: BaseDBModel
    template_path: str
    table_url: str
    can_edit_statuses: list[UserStatus]
    table_headers: list[str]
    create_url: str
    edit_url: str
    title: str

    def get(self, request):
        objects = self.model.all()
        user_status = UserStatus(request.COOKIES.get("user_status"))
        can_edit = user_status in self.can_edit_statuses
        context = {
            "objects": objects,
            "title": self.title,
            "create_url": self.create_url,
            "edit_url": self.edit_url,
            "table_headers": self.table_headers,
            "table_url": self.table_url,
            "request_unique_fields": self.model.get_primary_fields(),
            "can_edit": can_edit,
        }
        return render(request, self.template_path, context)

    def post(self, request):
        data = [request.POST[field] for field in self.model.get_primary_fields()]
        obj = self.model.get(*data)
        obj.remove()
        return redirect(self.table_url)


class ProvidersView(BaseTableView):
    model = Database.Provider
    template_path = "my_app/tables/providers.html"
    table_url = "providers_url"
    table_headers = ["Код", "Название", "Адрес"]
    create_url = "create_provider_url"
    edit_url = "edit_provider_url"
    title = "Поставщики"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class FlowersView(BaseTableView):
    model = Database.Flower
    template_path = "my_app/tables/flowers.html"
    table_url = "flowers_url"
    table_headers = ["Код", "Название", "Цена за рассаду", "Код поставщика"]
    create_url = "create_flower_url"
    edit_url = "edit_flower_url"
    title = "Цветы"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT, UserStatus.PURCHASE_MANAGER,
                        UserStatus.DELIVERY_MANAGER, UserStatus.CUSTOMER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class CustomersView(BaseTableView):
    model = Database.Customer
    template_path = "my_app/tables/customers.html"
    table_url = "customers_url"
    table_headers = ["Код", "Название", "Телефон", "Адрес"]
    create_url = "create_customer_url"
    edit_url = "edit_customer_url"
    title = "Заказчики"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.DELIVERY_MANAGER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class ContractsView(BaseTableView):
    model = Database.Contract
    template_path = "my_app/tables/contracts.html"
    table_url = "contracts_url"
    table_headers = ["Код договора", "Код заказчика", "Дата регистрации", "Дата исполнения"]
    create_url = "create_contract_url"
    edit_url = "edit_contract_url"
    title = "Договоры"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT, UserStatus.PURCHASE_MANAGER,
                        UserStatus.DELIVERY_MANAGER, UserStatus.CUSTOMER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER, UserStatus.CUSTOMER]


class OrdersView(BaseTableView):
    model = Database.Order
    template_path = "my_app/tables/orders.html"
    table_url = "contracts_url"
    table_headers = ["Код", "Код договора", "Код цветка", "Количество рассады"]
    create_url = "create_order_url"
    edit_url = "edit_order_url"
    title = "Заказы"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT, UserStatus.PURCHASE_MANAGER,
                        UserStatus.DELIVERY_MANAGER, UserStatus.CUSTOMER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER, UserStatus.CUSTOMER]


class EmployeesView(BaseTableView):
    model = Database.Employee
    template_path = "my_app/tables/employees.html"
    table_url = "employees_url"
    table_headers = ["Логин", "Пароль", "Должность"]
    create_url = "register_employee_url"
    edit_url = "edit_employee_url"
    title = "Сотрудники"
    allowed_statuses = [UserStatus.HEAD_MANAGER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class CustomersUsersView(BaseTableView):
    model = Database.CustomerUser
    template_path = "my_app/tables/customers_users.html"
    table_url = "customers_users_url"
    table_headers = ["Логин", "Пароль", "Код заказчика"]
    create_url = "register_customer_url"
    edit_url = "edit_customer_url"
    title = "Аккаунты заказчиков"
    allowed_statuses = [UserStatus.HEAD_MANAGER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class BaseCreateView(UserStatusRequiredMixin, View):
    form_class: type[forms.BaseCreateForm]
    template_path: str
    redirect_url: str

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_path, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save_to_db()
            return redirect(self.redirect_url)
        else:
            return render(request, self.template_path, {"form": form})


class ProviderCreateView(BaseCreateView):
    form_class = forms.ProviderCreateForm
    template_path = "my_app/create/create_provider.html"
    redirect_url = "providers_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class FlowerCreateView(BaseCreateView):
    form_class = forms.FlowerCreateForm
    template_path = "my_app/create/create_flower.html"
    redirect_url = "flowers_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class CustomerCreateView(BaseCreateView):
    form_class = forms.CustomerCreateForm
    template_path = "my_app/create/create_customer.html"
    redirect_url = "customers_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class ContractCreateView(BaseCreateView):
    form_class = forms.ContractCreateForm
    template_path = "my_app/create/create_contract.html"
    redirect_url = "contracts_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class OrderCreateView(BaseCreateView):
    form_class = forms.OrderCreateForm
    template_path = "my_app/create/create_order.html"
    redirect_url = "orders_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class RegisterEmployeeForm(BaseCreateView):
    form_class = forms.EmployeeRegisterForm
    template_path = "my_app/users/register_employee.html"
    redirect_url = "employees_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class RegisterCustomerForm(BaseCreateView):
    form_class = forms.CustomerUserRegisterForm
    template_path = "my_app/users/register_customer.html"
    redirect_url = "customers_users_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class Commit(View):
    def post(self, request):
        Database.connection.connection.commit()
        prev_path = request.POST["curr_path"]
        return redirect(prev_path)


class Rollback(View):
    def post(self, request):
        Database.connection.connection.rollback()
        prev_path = request.POST["curr_path"]
        return redirect(prev_path)


class LoginView(View):
    def get(self, request):
        form = forms.LoginForm()
        return render(request, "my_app/users/login.html", {"form": form})

    def post(self, request):
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            login = form.cleaned_data["login"]
            password = form.cleaned_data["password"]
            try:
                user_status = UserManager.get_status(login, password)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                response = redirect("index_url")
                response.set_cookie("user_status", user_status.value)
                return response
        return render(request, "my_app/users/login.html", {"form": form})


class ExitView(View):
    def get(self, request):
        response = redirect("index_url")
        response.delete_cookie("user_status")
        return response


class BaseUpdateView(View):
    model: BaseDBModel
    form_class: type[forms.BaseUpdateForm]
    title: str
    edit_url: str
    template_path: str
    redirect_url: str

    def get(self, request):
        primary_params = dict()
        for field in self.model.get_primary_fields():
            primary_params["__old_" + field] = request.GET[field]
        form = self.form_class(primary_params)
        context = {
            "form": form,
            "primary_params": primary_params,
            "title": self.title,
            "edit_url": self.edit_url
        }
        return render(request, self.template_path, context)

    def post(self, request):
        primary_params = dict()
        for field in self.model.get_primary_fields():
            primary_params[field] = request.POST["__old_" + field]
        form = self.form_class(primary_params, request.POST)
        if form.is_valid():
            form.save_to_db()
            return redirect(self.redirect_url)
        else:
            context = {
                "form": form,
                "primary_params": primary_params,
                "title": self.title,
                "edit_url": self.edit_url
            }
            return render(request, self.template_path, context)


class ProviderUpdateView(BaseUpdateView):
    model = Database.Provider
    form_class = forms.ProviderUpdateForm
    title = "Редактировать поставщика"
    edit_url = "edit_provider_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "providers_url"


class FlowerUpdateView(BaseUpdateView):
    model = Database.Flower
    form_class = forms.FlowerUpdateForm
    title = "Редактировать цветок"
    edit_url = "edit_flower_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "flowers_url"


class CustomerUpdateView(BaseUpdateView):
    model = Database.Customer
    form_class = forms.CustomerUpdateForm
    title = "Редактировать заказчика"
    edit_url = "edit_customer_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "customers_url"


class ContractUpdateView(BaseUpdateView):
    model = Database.Contract
    form_class = forms.ContractUpdateForm
    title = "Редактировать договор"
    edit_url = "edit_contract_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "contracts_url"


class OrderUpdateView(BaseUpdateView):
    model = Database.Order
    form_class = forms.OrderUpdateForm
    title = "Редактировать заказ"
    edit_url = "edit_order_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "orders_url"


class EmployeeUpdateView(BaseUpdateView):
    model = Database.Employee
    form_class = forms.EmployeeUpdateForm
    title = "Редактировать сотрудника"
    edit_url = "edit_employee_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "employees_url"


class CustomerUserUpdateView(BaseUpdateView):
    model = Database.CustomerUser
    form_class = forms.CustomerUserUpdateForm
    title = "Редактировать аккаунт заказчика"
    edit_url = "edit_customer_user_url"
    template_path = "my_app/update/base_update.html"
    redirect_url = "customers_users_url"
