class APIError(Exception):
    def __init__(self, code: int, message: str):
        super().__init__(message)
        self.code = code
    
    def __str__(self):
        return super().__str__()
