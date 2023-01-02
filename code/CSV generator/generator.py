import csv
from random import randint, shuffle

provider_names = open("providers.txt", encoding="utf-8").read().split("\n")
prov_count = len(provider_names)
shuffle(provider_names)

customer_names = open("customers.txt", encoding="utf-8").read().split("\n")
shuffle(customer_names)

phones = [randint(80000000000, 89999999999) for _ in range(len(customer_names) + 1)]
shuffle(phones)

addresses = open("addresses.txt", encoding="utf-8").read().split("\n")
shuffle(addresses)

flowers = open("flowers.txt", encoding="utf-8").read().split("\n")
shuffle(flowers)


def generate_providers():
    # id name address
    # id address
    i = 1
    fname_name = "csv/provider_name.csv"
    fname_address = "csv/provider_address.csv"
    with open(fname_name, "w", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        while provider_names:
            w.writerow((i, provider_names.pop()))
            i += 1

    with open(fname_address, "w", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        for j in range(1, i+1):
            w.writerow((j, addresses.pop()))


def generate_flowers():
    # id name price provider_id
    i = 1
    fname = "csv/flowers.csv"
    with open(fname, "w", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        while flowers:
            w.writerow((i, flowers.pop(), randint(5, 100), randint(1, prov_count)))
            i += 1


def generate_customers():
    # id name
    # id phone address
    i = 1
    fname_name = "csv/customer_name.csv"
    fname_info = "csv/customer_info.csv"
    with open(fname_name, "w", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        while customer_names:
            w.writerow((i, customer_names.pop()))
            i += 1

    with open(fname_info, "w", encoding="utf-8") as csvfile:
        w = csv.writer(csvfile)
        for j in range(1, i + 1):
            w.writerow((j, phones.pop(), addresses.pop()))


def main():
    generate_providers()
    generate_flowers()
    generate_customers()


main()