from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index_url"),
    path("commit", views.Commit.as_view(), name="commit_url"),
    path("rollback", views.Rollback.as_view(), name="rollback_url"),

    path("providers/", views.ProvidersView.as_view(), name="providers_url"),
    path("providers/create", views.ProviderCreateView.as_view(), name="create_provider_url"),
    path("providers/edit", views.ProviderUpdateView.as_view(), name="edit_provider_url"),

    path("flowers/", views.FlowersView.as_view(), name="flowers_url"),
    path("flowers/create", views.FlowerCreateView.as_view(), name="create_flower_url"),
    path("flowers/edit", views.FlowerUpdateView.as_view(), name="edit_flower_url"),

    path("customers/", views.CustomersView.as_view(), name="customers_url"),
    path("customers/create", views.CustomerCreateView.as_view(), name="create_customer_url"),
    path("customers/edit", views.CustomerUpdateView.as_view(), name="edit_customer_url"),

    path("contracts/", views.ContractsView.as_view(), name="contracts_url"),
    path("contracts/create", views.ContractCreateView.as_view(), name="create_contract_url"),
    path("contracts/edit", views.ContractUpdateView.as_view(), name="edit_contract_url"),

    path("orders/", views.OrdersView.as_view(), name="orders_url"),
    path("orders/create", views.OrderCreateView.as_view(), name="create_order_url"),
    path("orders/edit", views.OrderUpdateView.as_view(), name="edit_order_url"),

    path("employees/", views.EmployeesView.as_view(), name="employees_url"),
    path("employees/register", views.RegisterEmployeeForm.as_view(), name="register_employee_url"),
    path("employees/edit", views.EmployeeUpdateView.as_view(), name="edit_employee_url"),

    path("customers_users/", views.CustomersUsersView.as_view(), name="customers_users_url"),
    path("customers_users/register", views.RegisterCustomerForm.as_view(), name="register_customer_url"),
    path("customers_users/edit", views.CustomerUserUpdateView.as_view(), name="edit_customer_user_url"),

    path("login/", views.LoginView.as_view(), name="login_url"),
    path("exit/", views.ExitView.as_view(), name="exit_url")
]
