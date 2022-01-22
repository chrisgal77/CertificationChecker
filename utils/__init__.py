import datetime
import re

from .checkers import PEMSSLChecker, DERSSLChecker


def expire(cert_time: str, delta: int):
    cert_time = [int(element) for element in re.split(r"(:|-| )", cert_time)[::2]]
    cert_time = datetime.datetime(*cert_time)
    if (time_left := cert_time - datetime.datetime.today()) <= datetime.timedelta(seconds=delta):
        return True, time_left
    return False, None