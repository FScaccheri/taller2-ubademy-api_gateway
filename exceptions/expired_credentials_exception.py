class ExpiredCredentialsException(Exception):
    def __init__(self):
        self.message = "Credentials are expired"
