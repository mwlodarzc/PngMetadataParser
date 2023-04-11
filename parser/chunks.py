
from io import BufferedReader


CRITICAL_CHUNKS = ('IHDR',
                   'PLTE',
                   'IDAT',
                   'IEND')
"""
Take into consideration possibility of no inheritance and calling specific chunks in Chunk __init__
"""
class Chunk(object):
    def __init__(self, stream: BufferedReader) -> None:
        self.data_length = int.from_bytes(stream.read(4),'big')
        if self.data_length > 2**31:
            raise ValueError('Chunk bytes length exceeded')
        self.type_code = stream.read(4).decode("utf-8")
        if self.type_code in CRITICAL_CHUNKS:
            self.data = eval(f'{self.type_code}({stream.read(self.data_length)})')
        else:
            self.data = stream.read(self.data_length)
        self.CRC = stream.read(4)


class IHDR:
    def __init__(self, data: bytes) -> None:
        try:
            self.width = int.from_bytes(data[:4],'big')
            self.height = int.from_bytes(data[4:8],'big')
            if self.width == 0 or self.height == 0: # or self.width > 2**31 or self.height > 2**31:
                raise ValueError(f'{self.__class__.__name__}: Resolution')
            self.bit_depth, self.color_type, self.compression, self.filter, self.interlace = data[8:14]
            if self.bit_depth not in (1,2,4,8,16): #6???
                raise ValueError('Bit depth')
            if self.color_type not in (0,2,3,4,6):
                raise ValueError('Color type')
        except ValueError as err:
            print(type(err), f'{self.__class__.__name__}: {err}')
            
            
class PLTE: #?
    def __init__(self, data: bytes) -> None:
        try:
            if len(data) % 3:
                raise IndexError('Palette entries')
            self.palette = [tuple(r,g,b) for (r,g,b) in data]
            # print(self.palette)
        except IndexError as err:
            print(type(err), f'{self.__class__.__name__}: {err}')
            
class IDAT:
    def __init__(self, data: bytes) -> None:
        try:
            self.data = data
        except IndexError as err:
            print(type(err), f'{self.__class__.__name__}: {err}')
        
class IEND:
    def __init__(self, data: bytes) -> None:
        try:
            self.data = data
            # print(self.data)
        except IndexError as err:
            print(type(err), f'{self.__class__.__name__}: {err}')
        