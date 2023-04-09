import chunks
import matplotlib.pyplot as plt

PNG_SIGNATURE = 'PNG'

class ImagePNG(object):
    def __init__(self, filename) -> None:
        self.chunks = []
        try:
            self.file = open(filename, 'rb')
            signature = self.file.read(8)
            if signature[1:4].decode("utf-8") != PNG_SIGNATURE:
                raise ValueError('PNG signature doesn\'t match')
            self.chunks = [chunks.Chunk(self.file)]
            print(self.chunks[-1].type_code)
            while self.chunks[-1].type_code != 'IEND':
                self.chunks.append(chunks.Chunk(self.file))
                print(self.chunks[-1].type_code)
                # chunk = chunks.Chu    nk(self.file)
                # print(chunk.type_code.decode("utf-8"))
                # self.chunks.append(eval())
            self.chunks.append(chunks.IEND(self.file))
            print(self.chunks[-1].type_code)
            # self.IDAT = IDAT(self.file,(self.IHDR.width,self.IHDR.height),self.IHDR.bit_depth)
        except OSError as err:
            print(type(err), f'OS error: {err}')
        except ValueError as err:
            print(type(err), f'PNG load error: {err}')
            
    def show() -> None:
        # plt.plot(self.IDAT.)
        plt.axis('off')
        plt.show()
