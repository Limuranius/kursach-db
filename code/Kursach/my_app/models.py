import mysql.connector
from mysql.connector import CMySQLConnection
from mysql.connector.connection_cext import CMySQLCursor
from .model_objects import *


class BaseDBModel:
    mysql: CMySQLCursor

    def __init__(self, cursor):
        self.mysql = cursor

    def create(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def remove(self, *args, **kwargs):
        pass

    def all(self, *args, **kwargs):
        pass


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
    def create(self, name: str, price: int, provider_id: int):
        self.mysql.execute("""
            INSERT INTO flower(name, price, provider_id)
            VALUES (%s, %s, %s)
        """, (name, price, provider_id))

    def remove(self, flower_id: int):
        self.mysql.execute("""
            DELETE FROM flower
            WHERE flower_id = %s
        """, (flower_id,))

    def all(self) -> list[FlowerObj]:
        self.mysql.execute("""
            SELECT * FROM flower
        """)
        res = []
        for fields in self.mysql.fetchall():
            res.append(FlowerObj(*fields))
        return res

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
    def create(self, customer_id: int, register_date: datetime.date, execution_date: datetime.date):
        self.mysql.execute("""
            INSERT INTO contract(customer_id, register_date, execution_date)
            VALUES(%s, %s, %s)
        """, (customer_id, register_date, execution_date))

    def remove(self, contract_id: int):
        self.mysql.execute("""
            DELETE FROM contract
            WHERE contract_id = %s
        """, (contract_id,))

    def all(self) -> list[ContractObj]:
        self.mysql.execute("""
            SELECT * FROM contract
        """)
        res = []
        for fields in self.mysql.fetchall():
            res.append(ContractObj(*fields))
        return res

    def all_ids(self) -> list[int]:
        self.mysql.execute("""
            SELECT contract_id
            FROM contract
        """)
        return [row[0] for row in self.mysql.fetchall()]


class _Order(BaseDBModel):
    def create(self, contract_id: int, flower_id: int, quantity: int):
        self.mysql.execute("""
            INSERT INTO booking(contract_id, flower_id, quantity)
            VALUES(%s, %s, %s)
        """, (contract_id, flower_id, quantity))

    def remove(self, order_id: int):
        self.mysql.execute("""
            DELETE FROM booking
            WHERE booking_id = %s
        """, (order_id,))

    def all(self) -> list[OrderObj]:
        self.mysql.execute("""
            SELECT * FROM booking
        """)
        res = []
        for fields in self.mysql.fetchall():
            res.append(OrderObj(*fields))
        return res


class Database:
    Provider: _Provider
    Flower: _Flower
    Customer: _Customer
    Contract: _Contract
    Order: _Order
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
