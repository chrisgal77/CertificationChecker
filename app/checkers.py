from datetime import datetime
import json
import os
import subprocess


months_dict = {'Jan': 1,
               'Feb': 2,
               'Mar': 3,
               'Apr': 4,
               'May': 5,
               'Jun': 6,
               'Jul': 7,
               'Aug': 8,
               'Sep': 9,
               'Oct': 10,
               'Nov': 11,
               'Dec': 12}


def refactor_date(date):
    splitted_date = date.decode("utf-8").split()
    hours_minutes_seconds = splitted_date[7].split(":")
    return datetime(
        int(splitted_date[8]),
        months_dict[splitted_date[5][-3:]],
        int(splitted_date[6]),
        int(hours_minutes_seconds[0]),
        int(hours_minutes_seconds[1]),
        int(hours_minutes_seconds[2]),
    )


class Checker:
    port: int = 443
    name: str = "base"


class PEMSSLChecker(Checker):
    name: str = "PEM"

    def __init__(self):
        self.cache = self.read_pem_cache()

    def check_validity(self, server_name):
        process = subprocess.Popen(
            f"echo | openssl s_client -servername {server_name} -connect {server_name}:{self.port} | openssl x509 -noout -dates",
            shell=True,
            stdout=subprocess.PIPE,
        )
        output = process.stdout.read()
        return output

    def write_pem_cache(self):
        with open("pem_cache.json", "w") as f:
            json.dump(self.cache, f)

    def read_pem_cache(self):
        return json.load(open("pem_cache.json"))

    def check_cache(self):
        for idx, server_info in enumerate(self.cache["server_info"]):
            self.cache["server_info"][idx] = self.check(server_info['name'])

    def check(self, server_name):
        expiry_date = refactor_date(self.check_validity(server_name))
        print(f'{self.name} SSL Certificate expires at {expiry_date}')
        return {'name': server_name, 'expiry_date': str(expiry_date)}


class DERSSLChecker(Checker):
    name: str = "DER"

    def check_validity(self):
        ...
