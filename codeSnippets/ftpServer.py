from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import os

def run_ftp_server():
    # Tworzenie instancji autoryzatora
    authorizer = DummyAuthorizer()
    
    # Dodanie użytkownika (nazwa użytkownika, hasło, katalog domowy, uprawnienia)
    # Tutaj użytkownik 'user' z hasłem '12345' ma pełne uprawnienia do katalogu '/path/to/your/directory'
    authorizer.add_user('user', 'user', '/home/user/', perm='elradfmwMT')

    # Tworzenie uchwytu FTP i powiązanie z autoryzatorem
    handler = FTPHandler
    handler.authorizer = authorizer

    # Uruchomienie serwera na adresie 0.0.0.0 i porcie 21
    server = FTPServer(('0.0.0.0', 21), handler)
    server.serve_forever()

if __name__ == '__main__':
    run_ftp_server()

