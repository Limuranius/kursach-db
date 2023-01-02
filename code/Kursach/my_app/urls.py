from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index_url"),
    path("commit", views.Commit.as_view(), name="commit_url"),
    path("rollback", views.Rollback.as_view(), name="rollback_url"),

    path("providers/", views.ProvidersView.as_view(), name="providers_url"),
    path("providers/create", views.ProviderCreate.as_view(), name="create_provider_url"),

    path("flowers/", views.FlowersView.as_view(), name="flowers_url"),
    path("flowers/create", views.FlowerCreate.as_view(), name="create_flower_url"),

    path("customers/", views.CustomersView.as_view(), name="customers_url"),
    path("customers/create", views.CustomerCreate.as_view(), name="create_customer_url"),

    path("contracts/", views.ContractsView.as_view(), name="contracts_url"),
    path("contracts/create", views.ContractCreate.as_view(), name="create_contract_url"),

    path("orders/", views.OrdersView.as_view(), name="orders_url"),
    path("orders/create", views.OrderCreate.as_view(), name="create_order_url"),
]


