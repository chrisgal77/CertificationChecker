import argparse
import os
import time
import notifypy

from utils import PEMSSLChecker, DERSSLChecker, expire
from utils.checkers import BaseChecker


notifier = notifypy.Notify()


def _evaluate(checker: BaseChecker):
    for validation, name in checker.check_cache():
        expiry, time_left = expire(validation, args.period)
        if expiry:
            print(
                f"CERTIFICATE {name} EXPIRES IN LESS THAN {args.period} seconds! \n Time left: {time_left}"
            )
            notifier.title = "CERTIFICATE EXPIRY"
            notifier.message = f"CERTIFICATE {name} EXPIRES IN LESS THAN {args.period} seconds! \n Time left: {time_left}"
            notifier.application_name = "Certification checker"
            notifier.icon_path = os.path.join(
                os.path.dirname(__file__), "Attention-sign-icon.png"
            )
            notifier.send(block=False)

def interactive_mode():
    pem_validator = PEMSSLChecker()
    der_validator = DERSSLChecker()

    while True:
        print("============== INTERACTIVE MODE =============")
        print("a) check custom remote pem cert")
        print("b) check custom remote der cert")
        print("c) add and validate remote pem cert")
        print("d) add and validate remote der cert")
        print("e) add and validate local pem cert")
        print("f) add and validate local der cert")
        print("g) check cache for each")
        print("h) exit")
        print("=============================================")
        input_ = input()
        match input_:
            case "a":
                name = input("Server name:")
                pem_validator.check(name, "remote")
            case "b":
                name = input("Server name:")
                der_validator.check(name, "remote")
            case "c":
                name = input("Server name:")
                pem_validator.add_cert("remote", name)
            case "d":
                name = input("Server name")
                der_validator.add_cert("remote", name)
            case "e":
                name = input("PEM file path:")
                pem_validator.add_cert("local", name)
            case "f":
                name = input("DER file path:")
                der_validator.add_cert("local", name)
            case "g":
                print("#" * 30)
                print('CHECKING CACHE...')
                print("#" * 30)
                _evaluate(pem_validator)
                _evaluate(der_validator)
            case "h":
                break
        print("#" * 30)

    pem_validator.close()
    der_validator.close()


def get_args():
    parser = argparse.ArgumentParser(
        description="Flags for specific certification validation"
    )
    parser.add_argument("-i", "--interactive", help="The script runs in an interactive mode, where you can choose which mode to use", action="store_true", dest="i")
    parser.add_argument("-c", "--contiunous-running", help="The script runs contiunously checking cerificates every period", action="store_true", dest="c")
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