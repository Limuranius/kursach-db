from dataclasses import dataclass
import datetime


@dataclass
class ProviderObj:
    provider_id: int
    name: str
    address: str

    def __iter__(self):
        return iter([
            self.provider_id,
            self.name,
            self.address
        ])


@dataclass
class FlowerObj:
    flower_id: int
    name: str
    price: int
    provider_id: int

    def __iter__(self):
        return iter([
            self.flower_id,
            self.name,
            self.price,
            self.provider_id
        ])


@dataclass
class CustomerObj:
    customer_id: int
    name: str
    phone: str
    address: str

    def __iter__(self):
        return iter([
            self.customer_id,
            self.name,
            self.phone,
            self.address
        ])


@dataclass
class ContractObj:
    contract_id: int
    customer_id: int
    register_date: datetime.date
    execution_date: datetime.date

    def __iter__(self):
        return iter([
            self.contract_id,
            self.customer_id,
            self.register_date,
            self.execution_date
        ])


@dataclass
class OrderObj:
    order_id: int
    contract_id: int
    flower_id: int
    quantity: int

    def __iter__(self):
        return iter([
            self.order_id,
            self.contract_id,
            self.flower_id,
            self.quantity
        ])
