import argparse
import os
import time
from pprint import pp, pprint

import notifypy

from utils import DERSSLChecker, PEMSSLChecker, expire
from utils.checkers import BaseChecker

notifier = notifypy.Notify()


def _evaluate(checker: BaseChecker):
    for validation, name in checker.check_cache():
        print(name)
        expiry, time_left = expire(validation, args.period)
        if expiry:
            print(
                f"CERTIFICATE {name} EXPIRES IN LESS THAN {args.period} seconds! \n Time left: {time_left}"
            )
            notifier.title = "CERTIFICATE EXPIRY"
            notifier.message = f"CERTIFICATE {name} EXPIRES IN LESS THAN {args.period} seconds! \n Time left: {time_left}"
            notifier.application_name = "Certification checker"
            notifier.send(block=False)


def interactive_mode():
    pem_validator = PEMSSLChecker()
    der_validator = DERSSLChecker()

    while True:
        print("#" * 30)
        print("INTERACTIVE MODE ")
        print("a) check remote ssl cert")
        print("b) add and validate remote cert")
        print("c) add and validate local pem cert")
        print("d) add and validate local der cert")
        print("e) check cache for each")
        print("f) view cache")
        print("g) exit")
        print("#" * 30)
        input_ = input()
        match input_:
            case "a":
                name = input("Server name:")
                pem_validator.check(name, "remote")
                print("#" * 30)
            case "b":
                name = input("Server name:")
                pem_validator.add_cert("remote", name)
                print("#" * 30)
            case "c":
                name = input("PEM file path:")
                pem_validator.add_cert("local", name)
                print("#" * 30)
            case "d":
                name = input("DER file path:")
                der_validator.add_cert("local", name)
                print("#" * 30)
            case "e":
                print("#" * 30)
                print("CHECKING CACHE...")
                print("#" * 30)
                _evaluate(pem_validator)
                _evaluate(der_validator)
            case "f":
                print('PEM CHECKER')
                pprint(pem_validator.cache)
                print("DER CHECKER")
                pprint(der_validator.cache)
            case "g":
                print("#" * 30)
                break
        print("#" * 30)

    pem_validator.close()
    der_validator.close()


def get_args():
    parser = argparse.ArgumentParser(
        description="Script checks PEM and DER SSL certificates. Flags for specific certification validation:"
    )
    parser.add_argument(
        "-i",
        "--interactive",
        help="The script runs in an interactive mode, where you can choose which mode to use",
        action="store_true",
        dest="i",
    )
    parser.add_argument(
        "-c",
        "--contiunous-running",
        help="The script runs contiunously checking cached cerificates every period",
        action="store_true",
        dest="c",
    )
    parser.add_argument("-p", "--period", type=int, dest="period", default=86400)
    return parser.parse_args()


if __name__ == "__main__":

    args = get_args()

    if args.i:
        interactive_mode()
    elif args.c:
        checkers = [PEMSSLChecker(), DERSSLChecker()]
        while True:
            for checker in checkers:
                _evaluate(checker)
            time.sleep(args.period)
