import json
import os
import re
import subprocess
from abc import abstractmethod
from datetime import datetime
from typing import Dict

months_dict = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def refactor_date(date: bytes) -> datetime:
    date = date.decode("utf-8")
    date = re.search(
        r"notAfter=(...) (.?\d) (\d{2}):(\d{2}):(\d{2}) (\d{4}) GMT", date, re.MULTILINE
    )
    return str(
        datetime(
            int(date.group(6)),
            months_dict[date.group(1)],
            int(date.group(2)),
            int(date.group(3)),
            int(date.group(4)),
            int(date.group(5)),
        )
    )


class BaseChecker:
    port: int = 443
    name: str = "base"

    def __init__(self, cache_file: str):

        self.cache_file = cache_file
        if os.path.exists(cache_file):
            self.cache = self.read_cache()
            print(f"LOADED {self.name} CACHE...")
        else:
            self.cache = {"remote": [], "local": []}
            print(f"LOADED EMPTY {self.name} CACHE...")

    def check_remote_validity(self, name: str) -> bytes:
        process = subprocess.Popen(
            f"echo | openssl s_client -servername {name} -connect {name}:{self.port} | openssl x509 -noout -dates",
            shell=True,
            stdout=subprocess.PIPE,
        )
        output = process.stdout.read()
        return output

    def write_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def read_cache(self) -> Dict:
        return json.load(open(self.cache_file))

    def check_cache(self):
        print(f"CHECKING {self.name} CACHE")
        for key, value in self.cache.items():
            for idx, element in enumerate(value):
                validation = self.check(element["name"], key)["expiry_date"]
                if validation:
                    self.cache[key][idx] = {
                        "name": element["name"],
                        "expiry_date": validation,
                    }
                    yield validation, element["name"]

    def check(self, name: str, split: str) -> Dict:
        try:
            if split == "remote":
                expiry_date = refactor_date(self.check_remote_validity(name))
            elif split == "local":
                expiry_date = refactor_date(self.check_local_validity(name))

            print(f"{self.name} SSL Certificate for {name} expires at {expiry_date}")
            return {"name": name, "expiry_date": expiry_date}
        except Exception as e:
            print('Invalid server name or server has no certificate')
            return {"name": None, "expiry_date": None}

    def add_cert(self, split: str, name: str):
        try:
            if split == "remote":
                self.cache["remote"] = self.cache["remote"] + [self.check(name, "remote")]
            else:
                self.cache["local"] = self.cache["local"] + [self.check(name, "local")]
        except Exception as e:
            print('Invalid server name or server has no certificate')

    @abstractmethod
    def check_local_validity(self, cert_file: str) -> bytes:
        pass

    def close(self):
        self.write_cache()
        print(f"SUCCESSFULLY SAVED {self.name} CACHE")


class PEMSSLChecker(BaseChecker):
    name: str = "PEM"

    def __init__(self, cache_file: str = "pem_cache.json"):
        super().__init__(cache_file)

    def check_local_validity(self, cert_file: str) -> bytes:
        process = subprocess.Popen(
            f"echo | openssl x509 -enddate -noout -in {cert_file}",
            shell=True,
            stdout=subprocess.PIPE,
        )
        output = process.stdout.read()
        return output


class DERSSLChecker(BaseChecker):
    name: str = "DER"

    def __init__(self, cache_file: str = "der_cache.json"):
        super().__init__(cache_file)

    def check_local_validity(self, cert_file: str) -> bytes:
        process = subprocess.Popen(
            f"echo | openssl x509 -enddate -noout -inform DER -in {cert_file}",
            shell=True,
            stdout=subprocess.PIPE,
        )
        output = process.stdout.read()
        return output
