class WaisseBaseException(Exception):
    text = ''

    def __init__(self, message=None):
        if message:
            exception_content = f'{self.text}'
        else:
            exception_content = f'{self.text}: {message}'
        super().__init__(exception_content)


class InvalidConfig(Exception):
    """
    Exception raised when a configuration is bad formatted
    """
    text = 'The given configuration is invalid'
