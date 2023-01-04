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
    delete_request_fields: list[str]
    table_url: str
    can_edit_statuses: list[UserStatus]

    def get(self, request):
        objects = self.model.all()
        user_status = UserStatus(request.COOKIES.get("user_status"))
        can_edit = user_status in self.can_edit_statuses
        return render(request, self.template_path, context={"objects": objects, "can_edit": can_edit})

    def post(self, request):
        data = [request.POST[field] for field in self.delete_request_fields]
        self.model.remove(*data)
        return redirect(self.table_url)


class ProvidersView(BaseTableView):
    model = Database.Provider
    template_path = "my_app/providers.html"
    delete_request_fields = ["provider_id", "address"]
    table_url = "providers_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class FlowersView(BaseTableView):
    model = Database.Flower
    template_path = "my_app/flowers.html"
    delete_request_fields = ["flower_id"]
    table_url = "flowers_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT, UserStatus.PURCHASE_MANAGER,
                        UserStatus.DELIVERY_MANAGER, UserStatus.CUSTOMER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class CustomersView(BaseTableView):
    model = Database.Customer
    template_path = "my_app/customers.html"
    delete_request_fields = ["customer_id", "phone"]
    table_url = "customers_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.DELIVERY_MANAGER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class ContractsView(BaseTableView):
    model = Database.Contract
    template_path = "my_app/contracts.html"
    delete_request_fields = ["contract_id"]
    table_url = "contracts_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT, UserStatus.PURCHASE_MANAGER,
                        UserStatus.DELIVERY_MANAGER, UserStatus.CUSTOMER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER, UserStatus.CUSTOMER]


class OrdersView(BaseTableView):
    model = Database.Order
    template_path = "my_app/orders.html"
    delete_request_fields = ["order_id"]
    table_url = "contracts_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER, UserStatus.ACCOUNTANT, UserStatus.PURCHASE_MANAGER,
                        UserStatus.DELIVERY_MANAGER, UserStatus.CUSTOMER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER, UserStatus.CUSTOMER]


class EmployeesView(BaseTableView):
    model = Database.Employee
    template_path = "my_app/employees.html"
    delete_request_fields = ["login"]
    table_url = "employees_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]
    can_edit_statuses = [UserStatus.HEAD_MANAGER]


class CustomersUsersView(BaseTableView):
    model = Database.CustomerUser
    template_path = "my_app/customers_users.html"
    delete_request_fields = ["login"]
    table_url = "customers_users_url"
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
    form_class = forms.CustomerRegisterForm
    template_path = "my_app/users/register_customer.html"
    redirect_url = "customers_users_url"
    allowed_statuses = [UserStatus.HEAD_MANAGER]


class Commit(View):
    def post(self, request):
        Database.connection.commit()
        prev_path = request.POST["curr_path"]
        return redirect(prev_path)


class Rollback(View):
    def post(self, request):
        Database.connection.rollback()
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
