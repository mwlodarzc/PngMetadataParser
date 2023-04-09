
from io import BufferedReader

CRITICAL_CHUNKS = ('IHDR',
                   'PLTE',
                   'IDAT',
                   'IEND')

class Chunk(object):
    def __init__(self, stream: BufferedReader) -> None:
        self.data_length = int.from_bytes(stream.read(4),'big')
        print(self.data_length)
        if self.data_length > 2**31:
            raise ValueError('Chunk bytes length exceeded')
        self.type_code = stream.read(4).decode("utf-8")
        self.data = stream.read(self.data_length)
        self.CRC = stream.read(4)
        print(self.CRC)
        