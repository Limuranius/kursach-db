from dataclasses import dataclass
import datetime
from enum import Enum
import mysql.connector
from mysql.connector import CMySQLConnection
from mysql.connector.connection_cext import CMySQLCursor


class UserStatus(Enum):
    HEAD_MANAGER = "Head manager"
    ACCOUNTANT = "Accountant"
    PURCHASE_MANAGER = "Purchase manager"
    DELIVERY_MANAGER = "Delivery manager"
    CUSTOMER = "Customer"
    ANONYMOUS = None


class Connection:
    connection: CMySQLConnection = None

    @classmethod
    def get_cursor(cls) -> CMySQLCursor:
        if cls.connection is None:
            cls.connection = mysql.connector.connect(
                user="root",
                password="aboba",
                host="database",
                port="3306",
                database="kursach"
            )
        return cls.connection.cursor()


class BaseModelObj:
    primary_field: str  # Определить, если одна таблица с одним главным ключом
    table_name: str  # Определить, если одна таблица
    mysql = Connection.get_cursor()

    def update(self, *new_params):
        # Метод для объектов с одной таблицей с одним главным ключом.
        # Если это не так, то переопределить
        set_fields = ",".join([f"{field} = %s" for field in self.get_manual_fields()])
        query = f"""
            UPDATE {self.table_name}
            SET {set_fields}
            WHERE {self.primary_field} = %s
        """
        primary_value = getattr(self, self.primary_field)
        self.mysql.execute(query, (*new_params, primary_value))

    def remove(self):
        # Метод для объектов с одной таблицей с одним главным ключом.
        # Если это не так, то переопределить
        query = f"""
            DELETE FROM {self.table_name}
            WHERE {self.primary_field} = %s
        """
        primary_value = getattr(self, self.primary_field)
        self.mysql.execute(query, primary_value)

    def __iter__(self):
        pass

    @staticmethod
    def get_manual_fields() -> list[str]:
        pass


@dataclass
class ProviderObj(BaseModelObj):
    provider_id: int
    name: str
    address: str

    def update(self, name: str, address: str):
        self.__update_name(name)
        self.__update_address(address)

    def __update_name(self, name: str):
        self.mysql.execute("""
            UPDATE provider_name
            SET name = %s
            WHERE provider_id = %s
        """, (name, self.provider_id))

    def __update_address(self, address: str):
        self.mysql.execute("""
            UPDATE provider_address
            SET address = %s
            WHERE provider_id = %s AND address = %s
        """, (address, self.provider_id, self.address))

    def remove(self):
        if self.__count_address() == 1:
            self.__remove_name()  # Если удаляем последний адрес, то удаляем также и всего поставщика
        else:
            self.__remove_address()

    def __count_address(self) -> int:
        self.mysql.execute("""
            SELECT COUNT(*) 
            FROM provider_address 
            WHERE provider_id = %s
        """, (self.provider_id,))
        count = self.mysql.fetchone()[0]
        return count

    def __remove_name(self):
        self.mysql.execute("""
            DELETE FROM provider_name
            WHERE provider_id = %s
        """, (self.provider_id,))

    def __remove_address(self):
        self.mysql.execute("""
            DELETE FROM provider_address
            WHERE provider_id = %s AND address = %s
        """, (self.provider_id, self.address))

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["name", "address"]

    def __iter__(self):
        return iter([
            self.provider_id,
            self.name,
            self.address
        ])


@dataclass
class FlowerObj(BaseModelObj):
    primary_field = "flower_id"
    table_name = "flower"

    flower_id: int
    name: str
    price: int
    provider_id: int

    def update(self, name: str, price: int, provider_id: int):
        super().update(name, price, provider_id)

    def __iter__(self):
        return iter([
            self.flower_id,
            self.name,
            self.price,
            self.provider_id
        ])

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["name", "price", "provider_id"]


@dataclass
class CustomerObj(BaseModelObj):
    customer_id: int
    name: str
    phone: str
    address: str

    def update(self, name, phone, address):
        self.__update_name(name)
        self.__update_info(phone, address)

    def __update_name(self, name: str):
        self.mysql.execute("""
            UPDATE customer_name
            SET name = %s
            WHERE customer_id = %s
        """, (name, self.customer_id))

    def __update_info(self, phone: str, address: str):
        self.mysql.execute("""
            UPDATE customer_info
            SET phone = %s AND address = %s
            WHERE customer_id = %s AND phone = %s
        """, (phone, address, self.customer_id, self.phone))

    def remove(self):
        if self.__count_info() == 1:
            self.__remove_name()  # Если удаляем последнюю информацию, то удаляем также и всего заказчика
        else:
            self.__remove_info()

    def __count_info(self) -> int:
        self.mysql.execute("""
            SELECT COUNT(*)
            FROM customer_info
            WHERE customer_id = %s
        """, (self.customer_id,))
        return self.mysql.fetchone()[0]

    def __remove_name(self):
        self.mysql.execute("""
            DELETE FROM customer_name
            WHERE customer_id = %s
        """, (self.customer_id,))

    def __remove_info(self):
        self.mysql.execute("""
            DELETE FROM customer_info
            WHERE customer_id = %s AND phone = %s
        """, (self.customer_id, self.phone))

    def __iter__(self):
        return iter([
            self.customer_id,
            self.name,
            self.phone,
            self.address
        ])

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["name", "phone", "address"]


@dataclass
class ContractObj(BaseModelObj):
    primary_field = "contract_id"
    table_name = "contract"

    contract_id: int
    customer_id: int
    register_date: datetime.date
    execution_date: datetime.date

    def update(self, customer_id: int, register_date: datetime.date, execution_date: datetime.date):
        super().update(customer_id, register_date, execution_date)

    def __iter__(self):
        return iter([
            self.contract_id,
            self.customer_id,
            self.register_date,
            self.execution_date
        ])

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["customer_id", "register_date", "execution_date"]


@dataclass
class OrderObj(BaseModelObj):
    primary_field = "booking_id"
    table_name = "booking"

    booking_id: int
    contract_id: int
    flower_id: int
    quantity: int

    def update(self, contract_id: int, flower_id: int, quantity: int):
        super().update(contract_id, flower_id, quantity)

    def __iter__(self):
        return iter([
            self.booking_id,
            self.contract_id,
            self.flower_id,
            self.quantity
        ])

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["contract_id", "flower_id", "quantity"]


@dataclass
class EmployeeObj(BaseModelObj):
    primary_field = "login"
    table_name = "employee"

    login: str
    password: str
    job_title: str

    def update(self, login: str, password: str, job_title: str):
        super().update(login, password, job_title)

    def __iter__(self):
        return iter([
            self.login,
            self.password,
            self.job_title,
        ])

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["login", "password", "job_title"]


@dataclass
class CustomerUserObj(BaseModelObj):
    primary_field = "login"
    table_name = "customer_user"

    login: str
    password: str
    customer_id: int

    def update(self, login: str, password: str, customer_id: int):
        super().update(login, password, customer_id)

    def __iter__(self):
        return iter([
            self.login,
            self.password,
            self.customer_id,
        ])

    @staticmethod
    def get_manual_fields() -> list[str]:
        return ["login", "password", "customer_id"]
