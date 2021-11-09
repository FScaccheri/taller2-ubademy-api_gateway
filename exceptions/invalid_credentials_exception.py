class InvalidCredentialsException(Exception):
    def __init__(self):
        self.message = "Credentials are invalid"
