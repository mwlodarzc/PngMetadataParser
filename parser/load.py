from chunks import Chunk
import matplotlib.pyplot as plt
import zlib
import numpy as np

PNG_SIGNATURE = 'PNG'
def paeth_predictor(a,b,c):
    p = a+b-c
    pa,pb,pc = abs(p-a),abs(p-b),abs(p-c)
    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    else:
        return c
class ImagePNG(object):
    
    def __init__(self, filename) -> None:
        try:
            file = open(filename, 'rb')
            signature = file.read(8)
            if signature[1:4].decode("utf-8") != PNG_SIGNATURE:
                raise ValueError('PNG signature doesn\'t match')
        except OSError as err:
            print(type(err), f'OS error: {err}')
        except ValueError as err:
            print(type(err), f'PNG load error: {err}')
        
        try:
            self.chunks = [Chunk(file)]
            while self.chunks[-1].type_code != 'IEND':
                self.chunks.append(Chunk(file))
            self.chunks.append(Chunk(file))
        except Exception as err:
            print(type(err), f'Chunks: {err}')
            

        
    def __concatenate_data(self):
        self.byte_image = b''.join(map(lambda x:x.data,self.__seek('IDAT')))

    def __seek(self, chunk_type: str) -> list:
        return [c.data for c in self.chunks if c.type_code == chunk_type]
    
    def __decompress(self):
        self.__concatenate_data()
        self.image = zlib.decompress(self.byte_image)
        self.pixel_size = int((len(self.image)/self.chunks[0].data.height-1)/self.chunks[0].data.width)
        # print(self.chunks[0].data.bit_depth)
        
        # print(len(self.image))
        # print( self.chunks[0].data.height,self.chunks[0].data.width)
        
        # print( self.chunks[0].data.height * (1 + self.chunks[0].data.width * pixel_size))
        
        if len(self.image) != self.chunks[0].data.height * (1 + self.chunks[0].data.width * self.pixel_size):
            raise ValueError('Image size error')
        
        stride = self.chunks[0].data.width * self.pixel_size
        Recon = []
        recon_a = lambda r,c: Recon[r*stride+c-self.pixel_size] if c >=self.pixel_size else 0
        recon_b = lambda r,c: Recon[(r-1)*stride+c] if r>0 else 0 
        recon_c = lambda r,c: Recon[(r-1)*stride+c-self.pixel_size] if r> 0 and c>= self.pixel_size else 0 
        
        i = 0
        for r in range(self.chunks[0].data.height):
            filter_type = self.image[i]
            i+=1
            for c in range(stride):
                filter_x = self.image[i]
                i+=1
                if filter_type == 0:
                    recon_x = filter_x
                elif filter_type == 1:
                    recon_x = filter_x + recon_a(r,c)
                elif filter_type == 2:
                    recon_x = filter_x + recon_b(r,c)
                elif filter_type == 3:
                    recon_x = filter_x + (recon_a(r,c) + recon_b(r,c))// 2
                elif filter_type == 4:
                    recon_x = filter_x + paeth_predictor(recon_a(r,c),recon_b(r,c),recon_c(r,c))
                else:
                    raise NameError(f'filter unknown: {filter_type}')
                Recon.append(recon_x & 0xff)
                
        self.parsed_image = Recon
                
            
        
    def show(self) -> None:
        self.__decompress()
        plt.imshow(np.array(self.parsed_image).reshape((self.chunks[0].data.height,self.chunks[0].data.width,self.pixel_size)))
        plt.axis('off')
        plt.show()


