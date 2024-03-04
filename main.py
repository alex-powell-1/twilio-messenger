from messenger import MessengerWindow
from login import LoginWindow

r"""
 ___  __  __  ___    __  __  ____  ___  ___  ____  _  _  ___  ____  ____ 
/ __)(  \/  )/ __)  (  \/  )( ___)/ __)/ __)( ___)( \( )/ __)( ___)(  _ \
\__ \ )    ( \__ \   )    (  )__) \__ \\__ \ )__)  )  (( (_-. )__)  )   /
(___/(_/\/\_)(___/  (_/\/\_)(____)(___/(___/(____)(_)\_)\___/(____)(_)\_)

Authored by: Alex Powell
December 15, 2023
Version: 1
"""


def application():
    LoginWindow()
    MessengerWindow()


application()
