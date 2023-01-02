from django.shortcuts import render, redirect
from .models import Database, BaseDBModel
from django.views import View
from . import forms


class IndexView(View):
    def get(self, request):
        return render(request, "my_app/index.html")


class BaseTableView(View):
    model: BaseDBModel
    template_path: str

    def get(self, request):
        objects = self.model.all()
        return render(request, self.template_path, context={"objects": objects})


class ProvidersView(BaseTableView):
    model = Database.Provider
    template_path = "my_app/providers.html"

    def post(self, request):
        provider_id = request.POST["provider_id"]
        address = request.POST["address"]
        self.model.remove(provider_id, address)
        return redirect("providers_url")


class ProviderCreate(View):
    def get(self, request):
        form = forms.ProviderForm()
        return render(request, "my_app/create/create_provider.html", {"form": form})

    def post(self, request):
        form = forms.ProviderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            address = form.cleaned_data["address"]
            Database.Provider.create(name, address)
        else:
            return render(request, "my_app/create/create_provider.html", {"form": form})
        return redirect("providers_url")


class FlowersView(BaseTableView):
    model = Database.Flower
    template_path = "my_app/flowers.html"

    def post(self, request):
        flower_id = request.POST["flower_id"]
        self.model.remove(flower_id)
        return redirect("flowers_url")


class FlowerCreate(View):
    def get(self, request):
        form = forms.FlowerForm()
        form.set_providers(Database.Provider.all_names())
        return render(request, "my_app/create/create_flower.html", {"form": form})

    def post(self, request):
        form = forms.FlowerForm(request.POST)
        form.set_providers(Database.Provider.all_names())
        if form.is_valid():
            name = form.cleaned_data["name"]
            price = form.cleaned_data["price"]
            provider_name = form.cleaned_data["provider_name"]
            provider_id = Database.Provider.get_provider_id(provider_name)
            Database.Flower.create(name, price, provider_id)
        else:
            return render(request, "my_app/create/create_flower.html", {"form": form})
        return redirect("flowers_url")


class CustomersView(BaseTableView):
    model = Database.Customer
    template_path = "my_app/customers.html"

    def post(self, request):
        customer_id = request.POST["customer_id"]
        phone = request.POST["phone"]
        self.model.remove(customer_id, phone)
        return redirect("customers_url")


class CustomerCreate(View):
    def get(self, request):
        form = forms.CustomerForm()
        return render(request, "my_app/create/create_customer.html", {"form": form})

    def post(self, request):
        form = forms.CustomerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            phone = form.cleaned_data["phone"]
            address = form.cleaned_data["address"]
            Database.Customer.create(name, phone, address)
        else:
            return render(request, "my_app/create/create_customer.html", {"form": form})
        return redirect("customers_url")


class ContractsView(BaseTableView):
    model = Database.Contract
    template_path = "my_app/contracts.html"

    def post(self, request):
        contract_id = request.POST["contract_id"]
        self.model.remove(contract_id)
        return redirect("contracts_url")


class ContractCreate(View):
    def get(self, request):
        form = forms.ContractForm()
        form.set_customers(Database.Customer.all_names())
        return render(request, "my_app/create/create_contract.html", {"form": form})

    def post(self, request):
        form = forms.ContractForm(request.POST)
        form.set_customers(Database.Customer.all_names())
        if form.is_valid():
            customer_name = form.cleaned_data["customer_name"]
            register_date = form.cleaned_data["register_date"]
            execution_date = form.cleaned_data["execution_date"]
            customer_id = Database.Customer.get_customer_id(customer_name)
            Database.Contract.create(customer_id, register_date, execution_date)
        else:
            return render(request, "my_app/create/create_contract.html", {"form": form})
        return redirect("contracts_url")


class OrdersView(BaseTableView):
    model = Database.Order
    template_path = "my_app/orders.html"

    def post(self, request):
        order_id = request.POST["order_id"]
        self.model.remove(order_id)
        return redirect("contracts_url")


class OrderCreate(View):
    def get(self, request):
        form = forms.OrderForm()
        form.set_contracts(Database.Contract.all_ids())
        form.set_flowers(Database.Flower.all_names())
        return render(request, "my_app/create/create_order.html", {"form": form})

    def post(self, request):
        form = forms.OrderForm(request.POST)
        form.set_contracts(Database.Contract.all_ids())
        form.set_flowers(Database.Flower.all_names())
        if form.is_valid():
            contract_id = form.cleaned_data["contract_id"]
            flower_name = form.cleaned_data["flower_name"]
            quantity = form.cleaned_data["quantity"]
            flower_id = Database.Flower.get_flower_id(flower_name)
            Database.Order.create(contract_id, flower_id, quantity)
        else:
            return render(request, "my_app/create/create_order.html", {"form": form})
        return redirect("orders_url")


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
