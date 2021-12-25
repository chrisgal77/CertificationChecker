import argparse

from utils import PEMSSLChecker, DERSSLChecker


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
        print("g) chech cache for each")
        print("h) exit")
        print("=============================================")
        input_ = input()
        match input_:
            case 'a':
                name = input("Server name:")
                pem_validator.check(name, 'remote')
            case 'b':
                name = input("Server name:")
                der_validator.check(name, 'remote')
            case 'c':
                name = input("Server name:")
                pem_validator.add_cert('remote', name)
            case 'd':
                name = input("Server name")
                der_validator.add_cert('remote', name)
            case 'e':
                name = input("PEM file path:")
                pem_validator.add_cert('local', name)
            case 'f':
                name = input("DER file path:")
                der_validator.add_cert('local', name)
            case 'g':
                der_validator.check_cache()
                pem_validator.check_cache()
            case 'h':
                break

    pem_validator.close()
    der_validator.close()

def get_args():
    parser = argparse.ArgumentParser(description="Flags for specific certification validation")
    parser.add_argument(
        '-i',
        '--interactive',
        action='store_true',
        dest='i'
    )
    parser.add_argument(
        '-p',
        '--pem',
        action='store_true',
        dest='pem'
    )
    parser.add_argument(
        '-d',
        '--der',
        action='store_true',
        dest='der'
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    if args.i:
        interactive_mode()
    else:
        checkers = [PEMSSLChecker(), DERSSLChecker()]
        for checker in checkers:
            checker.check_cache()
            checker.close()