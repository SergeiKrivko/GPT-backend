class ExtractFailedError(ValueError):
    def __init__(self, message):
        self.__message = message

    def __str__(self):
        return f'Text extraction failed: {self.__message}'
