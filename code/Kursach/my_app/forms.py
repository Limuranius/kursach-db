from django import forms


class ProviderForm(forms.Form):
    name = forms.CharField(label="Название поставщика", max_length=50)
    address = forms.CharField(label="Адрес поставщика", max_length=100)


class FlowerForm(forms.Form):
    name = forms.CharField(label="Название", max_length=50)
    price = forms.IntegerField(label="Цена за рассаду")
    provider_name = forms.ChoiceField(label="Поставщик")

    def set_providers(self, provider_names: list[str]):
        choices = [(name, name) for name in provider_names]
        self.fields["provider_name"].choices = choices


class CustomerForm(forms.Form):
    name = forms.CharField(label="Название заказчика", max_length=50)
    phone = forms.CharField(label="Телефон заказчика", max_length=50)
    address = forms.CharField(label="Адрес заказчика", max_length=100)


class ContractForm(forms.Form):
    customer_name = forms.ChoiceField(label="Заказчик")
    register_date = forms.DateField(label="Дата регистрации", widget=forms.DateInput({"type": "date"}))
    execution_date = forms.DateField(label="Дата исполнения", widget=forms.DateInput({"type": "date"}))

    def set_customers(self, customer_names: list[str]):
        choices = [(name, name) for name in customer_names]
        self.fields["customer_name"].choices = choices


class OrderForm(forms.Form):
    contract_id = forms.ChoiceField(label="Номер договора")
    flower_name = forms.ChoiceField(label="Название цветка")
    quantity = forms.IntegerField(label="Количество рассады")

    def set_contracts(self, contract_ids: list[int]):
        choices = [(contract_id, contract_id) for contract_id in contract_ids]
        self.fields["contract_id"].choices = choices

    def set_flowers(self, flower_names: list[str]):
        choices = [(name, name) for name in flower_names]
        self.fields["flower_name"].choices = choices
