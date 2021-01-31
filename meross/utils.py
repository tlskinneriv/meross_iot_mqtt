import base64
from typing import List

def mangle(s):
    return str(base64.b64encode(s.encode("utf-8")), "utf-8")

def valid_header(header: dict, valid_methods: List[str]):
    if ( header['method'] in valid_methods ):
        return True
    else:
        return False