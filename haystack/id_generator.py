import uuid


class IdGenerator:
    def __init__(self):
        pass

    def generate(self):
        """
        Generates a UUID
        """
        return format(uuid.uuid4())

    def generate_trace_id(self):
        """"
        Generates a b3 format compatible trace id
        """
        return self.__next_long()

    def generate_span_id(self):
        """"
        Generates a b3 format compatible span id
        """
        return self.__next_long()

    def __next_long(self):
        random_number = uuid.uuid4()
        while random_number.int == 0:
            random_number = uuid.uuid4()
        return random_number.hex
