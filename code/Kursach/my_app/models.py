from .model_objects import *


class BaseDBModel:
    mysql: CMySQLCursor

    def __init__(self, cursor):
        self.mysql = cursor

    def create(self, *args):
        raise NotImplementedError

    def all(self) -> list[BaseModelObj]:
        raise NotImplementedError

    def get(self, *primary_values) -> BaseModelObj:
        raise NotImplementedError

    def get_primary_fields(self) -> list[str]:
        raise NotImplementedError


class OneTableModel(BaseDBModel):
    primary_field: str
    manual_fields: list[str]
    table_name: str
    model_obj: type[BaseModelObj]

    def create(self, *args):
        query = f"""
            INSERT INTO {self.table_name}({",".join(self.manual_fields)})
            VALUES({",".join(["%s"] * len(self.manual_fields))})
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

    def get(self, primary_value) -> BaseModelObj:
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE {self.primary_field} = %s
        """
        self.mysql.execute(query, (primary_value,))
        return self.model_obj(*self.mysql.fetchone())

    def get_primary_fields(self) -> list[str]:
        return [self.primary_field]


class _Provider(BaseDBModel):
    primary_fields = ["provider_id", "address"]

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

    def get(self, provider_id, address):
        self.mysql.execute("""
                    SELECT provider_name.provider_id, provider_name.name, provider_address.address
                    FROM provider_name
                    JOIN provider_address
                    ON provider_name.provider_id = provider_address.provider_id
                    WHERE provider_name.provider_id = %s AND provider_address.address = %s
        """, (provider_id, address))
        return ProviderObj(*self.mysql.fetchone())

    def all_names(self) -> list[str]:
        self.mysql.execute("""
            SELECT name
            FROM provider_name
        """)
        return [row[0] for row in self.mysql.fetchall()]

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

    def get_primary_fields(self) -> list[str]:
        return self.primary_fields


class _Flower(OneTableModel):
    model_obj = FlowerObj
    table_name = FlowerObj.table_name
    primary_field = FlowerObj.primary_field
    manual_fields = FlowerObj.get_manual_fields()

    def create(self, name: str, price: int, provider_id: int):
        super().create(name, price, provider_id)

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
    primary_fields = ["customer_id", "phone"]

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

    def all_names(self) -> list[str]:
        self.mysql.execute("""
            SELECT name
            FROM customer_name
        """)
        return [row[0] for row in self.mysql.fetchall()]

    def get_primary_fields(self) -> list[str]:
        return self.primary_fields


class _Contract(OneTableModel):
    model_obj = ContractObj
    table_name = ContractObj.table_name
    manual_fields = ContractObj.get_manual_fields()
    primary_field = ContractObj.primary_field

    def create(self, customer_id: int, register_date: datetime.date, execution_date: datetime.date):
        return super().create(customer_id, register_date, execution_date)

    def all_ids(self) -> list[int]:
        self.mysql.execute("""
            SELECT contract_id
            FROM contract
        """)
        return [row[0] for row in self.mysql.fetchall()]


class _Order(OneTableModel):
    model_obj = OrderObj
    primary_field = OrderObj.primary_field
    table_name = OrderObj.table_name
    manual_fields = OrderObj.get_manual_fields()

    def create(self, contract_id: int, flower_id: int, quantity: int):
        super().create(contract_id, flower_id, quantity)


class _Employee(OneTableModel):
    model_obj = EmployeeObj
    table_name = EmployeeObj.table_name
    manual_fields = EmployeeObj.get_manual_fields()
    primary_field = EmployeeObj.primary_field

    def create(self, login: str, password: str, job_title: str):
        super().create(login, password, job_title)

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


class _CustomerUser(OneTableModel):
    model_obj = CustomerUserObj
    table_name = CustomerUserObj.table_name
    manual_fields = CustomerUserObj.get_manual_fields()
    primary_field = CustomerUserObj.primary_field

    def create(self, login: str, password: str, customer_id: int):
        super().create(login, password, customer_id)

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
    connection: type[Connection]

    @classmethod
    def init_models(cls):
        cls.connection = Connection
        cursor = Connection.get_cursor()
        cls.Provider = _Provider(cursor)
        cls.Flower = _Flower(cursor)
        cls.Customer = _Customer(cursor)
        cls.Contract = _Contract(cursor)
        cls.Order = _Order(cursor)
        cls.Employee = _Employee(cursor)
        cls.CustomerUser = _CustomerUser(cursor)
