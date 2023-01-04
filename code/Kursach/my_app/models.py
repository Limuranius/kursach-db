import mysql.connector
from mysql.connector import CMySQLConnection
from mysql.connector.connection_cext import CMySQLCursor
from .model_objects import *


class BaseDBModel:
    mysql: CMySQLCursor
    table_name: str
    manual_fields: list[str]
    primary_field: str
    model_obj: type

    def __init__(self, cursor):
        self.mysql = cursor

    def create(self, *args):
        query = f"""
            INSERT INTO {self.table_name}({",".join(self.manual_fields)})
            VALUES({",".join(["%s"] * len(self.manual_fields))})
        """
        self.mysql.execute(query, args)

    def update(self, *args, **kwargs):
        pass

    def remove(self, *args):
        query = f"""
            DELETE FROM {self.table_name}
            WHERE {self.primary_field} = %s
        """
        self.mysql.execute(query, args)

    def all(self):
        query = f"""
            SELECT * FROM {self.table_name}
        """
        self.mysql.execute(query)
        res = []
        for fields in self.mysql.fetchall():
            res.append(self.model_obj(*fields))
        return res


class _Provider(BaseDBModel):
    def create(self, name: str, address: str) -> None:
        if not self.__provider_exist(name):
            self.mysql.execute("""
                INSERT INTO provider_name(name)
                VALUES (%s)
            """, (name,))
        provider_id = self.get_provider_id(name)
        self.mysql.execute("""
            INSERT INTO provider_address(provider_id, address)
            VALUES (%s, %s)
        """, (provider_id, address))

    def all(self) -> list[ProviderObj]:
        self.mysql.execute("""
            SELECT provider_name.provider_id, provider_name.name, provider_address.address
            FROM provider_name
            JOIN provider_address
            ON provider_name.provider_id = provider_address.provider_id
        """)
        res = []
        for fields in self.mysql.fetchall():
            res.append(ProviderObj(*fields))
        return res

    def all_names(self) -> list[str]:
        self.mysql.execute("""
            SELECT name
            FROM provider_name
        """)
        return [row[0] for row in self.mysql.fetchall()]

    def remove(self, provider_id: int, address: str):
        if self.__count_address(provider_id) == 1:
            self.__remove_name(provider_id)  # Если удаляем последний адрес, то удаляем также и всего поставщика
        else:
            self.__remove_address(provider_id, address)

    def __count_address(self, provider_id: int) -> int:
        self.mysql.execute("""
                    SELECT COUNT(*) 
                    FROM provider_address 
                    WHERE provider_id = %s
                """, (provider_id,))
        count = self.mysql.fetchone()[0]
        return count

    def __provider_exist(self, name) -> bool:
        self.mysql.execute("""
            SELECT COUNT(*) 
            FROM provider_name 
            WHERE name = %s
        """, (name,))
        count = self.mysql.fetchone()[0]
        return count != 0

    def get_provider_id(self, name) -> int:
        self.mysql.execute("""
            SELECT provider_id
            FROM provider_name
            WHERE name = %s
        """, (name,))
        return self.mysql.fetchone()[0]

    def __remove_name(self, provider_id: int):
        self.mysql.execute("""
            DELETE FROM provider_name
            WHERE provider_id = %s
        """, (provider_id,))

    def __remove_address(self, provider_id: int, address: str):
        self.mysql.execute("""
            DELETE FROM provider_address
            WHERE provider_id = %s AND address = %s
        """, (provider_id, address))


class _Flower(BaseDBModel):
    table_name = "flower"
    manual_fields = ["name", "price", "provider_id"]
    primary_field = "flower_id"
    model_obj = FlowerObj

    def create(self, name: str, price: int, provider_id: int):
        super().create(name, price, provider_id)

    def remove(self, flower_id: int):
        super().remove(flower_id)

    def all(self) -> list[FlowerObj]:
        return super().all()

    def all_names(self) -> list[str]:
        self.mysql.execute("""
            SELECT name
            FROM flower
        """)
        return [row[0] for row in self.mysql.fetchall()]

    def get_flower_id(self, name: str) -> int:
        self.mysql.execute("""
            SELECT flower_id
            FROM flower
            WHERE name = %s
        """, (name,))
        return self.mysql.fetchone()[0]


class _Customer(BaseDBModel):
    def create(self, name: str, phone: str, address: str):
        if not self.__customer_exist(name):
            self.mysql.execute("""
                INSERT INTO customer_name(name)
                VALUES (%s)
            """, (name,))
        customer_id = self.get_customer_id(name)
        self.mysql.execute("""
            INSERT INTO customer_info(customer_id, phone, address)
            VALUES (%s, %s, %s)
        """, (customer_id, phone, address))

    def __customer_exist(self, name) -> bool:
        self.mysql.execute("""
            SELECT COUNT(*) 
            FROM customer_name 
            WHERE name = %s
        """, (name,))
        count = self.mysql.fetchone()[0]
        return count != 0

    def get_customer_id(self, name) -> int:
        self.mysql.execute("""
            SELECT customer_id
            FROM customer_name
            WHERE name = %s
        """, (name,))
        return self.mysql.fetchone()[0]

    def all(self) -> list[CustomerObj]:
        self.mysql.execute("""
                    SELECT customer_name.customer_id, customer_name.name, 
                        customer_info.phone, customer_info.address
                    FROM customer_name
                    JOIN customer_info
                    ON customer_name.customer_id = customer_info.customer_id
                """)
        res = []
        for fields in self.mysql.fetchall():
            res.append(CustomerObj(*fields))
        return res

    def all_names(self) -> list[str]:
        self.mysql.execute("""
            SELECT name
            FROM customer_name
        """)
        return [row[0] for row in self.mysql.fetchall()]

    def remove(self, customer_id: int, phone: str):
        if self.__count_info(customer_id) == 1:
            self.__remove_name(customer_id)  # Если удаляем последнюю информацию, то удаляем также и всего заказчика
        else:
            self.__remove_info(customer_id, phone)

    def __count_info(self, customer_id) -> int:
        self.mysql.execute("""
            SELECT COUNT(*)
            FROM customer_info
            WHERE customer_id = %s
        """, (customer_id,))
        return self.mysql.fetchone()[0]

    def __remove_name(self, customer_id: int):
        self.mysql.execute("""
            DELETE FROM customer_name
            WHERE customer_id = %s
        """, (customer_id,))

    def __remove_info(self, customer_id: int, phone: str):
        self.mysql.execute("""
            DELETE FROM customer_info
            WHERE customer_id = %s AND phone = %s
        """, (customer_id, phone))


class _Contract(BaseDBModel):
    table_name = "contract"
    manual_fields = ["customer_id", "register_date", "execution_date"]
    primary_field = "contract_id"
    model_obj = ContractObj

    def create(self, customer_id: int, register_date: datetime.date, execution_date: datetime.date):
        return super().create(customer_id, register_date, execution_date)

    def remove(self, contract_id: int):
        return super().remove(contract_id)

    def all(self) -> list[ContractObj]:
        return super().all()

    def all_ids(self) -> list[int]:
        self.mysql.execute("""
            SELECT contract_id
            FROM contract
        """)
        return [row[0] for row in self.mysql.fetchall()]


class _Order(BaseDBModel):
    table_name = "booking"
    manual_fields = ["contract_id", "flower_id", "quantity"]
    primary_field = "booking_id"
    model_obj = OrderObj

    def create(self, contract_id: int, flower_id: int, quantity: int):
        super().create(contract_id, flower_id, quantity)

    def remove(self, order_id: int):
        super().remove(order_id)

    def all(self) -> list[OrderObj]:
        return super().all()


class _Employee(BaseDBModel):
    table_name = "employee"
    manual_fields = ["login", "password", "job_title"]
    primary_field = "login"
    model_obj = EmployeeObj

    def create(self, login: str, password: str, job_title: str):
        super().create(login, password, job_title)

    def remove(self, login: str):
        super().remove(login)

    def all(self) -> list[EmployeeObj]:
        return super().all()

    def get(self, login: str) -> EmployeeObj | None:
        self.mysql.execute("""
            SELECT * FROM employee
            WHERE login = %s
        """, (login,))
        obj = self.mysql.fetchone()
        if obj is None:
            return None
        else:
            return EmployeeObj(*obj)


class _CustomerUser(BaseDBModel):
    table_name = "customer_user"
    manual_fields = ["login", "password", "customer_id"]
    primary_field = "login"
    model_obj = CustomerUserObj

    def create(self, login: str, password: str, customer_id: int):
        super().create(login, password, customer_id)

    def remove(self, login: str):
        super().remove(login)
    def all(self) -> list[CustomerObj]:
        return super().all()

    def get(self, login: str) -> CustomerUserObj | None:
        self.mysql.execute("""
            SELECT * FROM customer_user
            WHERE login = %s
        """, (login,))
        obj = self.mysql.fetchone()
        if obj is None:
            return None
        else:
            return CustomerUserObj(*obj)


class Database:
    Provider: _Provider
    Flower: _Flower
    Customer: _Customer
    Contract: _Contract
    Order: _Order
    Employee: _Employee
    CustomerUser: _CustomerUser
    connection: CMySQLConnection

    @classmethod
    def init_models(cls):
        connection = mysql.connector.connect(
            user="root",
            password="aboba",
            host="database",
            port="3306",
            database="kursach"
        )
        cursor = connection.cursor()

        cls.connection = connection
        cls.Provider = _Provider(cursor)
        cls.Flower = _Flower(cursor)
        cls.Customer = _Customer(cursor)
        cls.Contract = _Contract(cursor)
        cls.Order = _Order(cursor)
        cls.Employee = _Employee(cursor)
        cls.CustomerUser = _CustomerUser(cursor)
