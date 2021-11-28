from app.checkers import PEMSSLChecker

pem = PEMSSLChecker()
pem.check_cache()
pem.write_pem_cache()