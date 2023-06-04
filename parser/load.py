from chunks import Chunk, CRITICAL_CHUNKS, SUPPORTED_CHUNKS
import matplotlib.pyplot as plt
import zlib
import numpy as np
from random import randint

PNG_SIGNATURE = "PNG"


class ImagePNG(object):
    def __init__(self, filename) -> None:
        try:
            self.filename = filename
            file = open(self.filename, "rb")
            self.signature = file.read(8)
            if self.signature[1:4].decode("utf-8") != PNG_SIGNATURE:
                raise ValueError("PNG signature doesn't match")
        except OSError as err:
            print(type(err), f"OS error: {err}")
        except ValueError as err:
            print(type(err), f"PNG load error: {err}")

        IDAT_counter, chunk_address = 1, 8
        self.chunks = []
        try:
            while True:
                self.chunks.append(Chunk(file))
                self.chunks[-1].address = chunk_address
                chunk_address += self.chunks[-1].data_length
                if self.chunks[-1].type_code == "IDAT":
                    self.chunks[-1].info["counter"] = IDAT_counter
                    IDAT_counter += 1
                elif self.chunks[-1].type_code == "IEND":
                    break

        except Exception as err:
            print(type(err), f"Chunks: {err}")

    @staticmethod
    def __paeth_predictor(a, b, c):
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c

    @staticmethod
    def __calculate_crc(data: bytes):
        crc = zlib.crc32(data)
        return (crc & 0xFFFFFFFF).to_bytes(4, "big")

    def __concatenate_data(self):
        self.byte_image = b"".join(map(lambda x: x.binary_data, self.__seek("IDAT")))

    def __seek(self, chunk_type: str) -> list:
        return [c for c in self.chunks if c.type_code == chunk_type]

    def __compress(self) -> list:
        stride = self.chunks[0].info["width"] * self.pixel_size
        Filtered = []
        orig_a = (
            lambda r, c: Filtered[r * stride + c - self.pixel_size]
            if c >= self.pixel_size
            else 0
        )
        orig_b = lambda r, c: Filtered[(r - 1) * stride + c] if r > 0 else 0
        orig_c = (
            lambda r, c: Filtered[(r - 1) * stride + c - self.pixel_size]
            if r > 0 and c >= self.pixel_size
            else 0
        )

        i = 0
        for r in range(self.chunks[0].info["height"]):
            filter_type = randint(0, 4)
            i += 1
            for c in range(stride):
                orig_x = self.byte_image[i]
                i += 1
                if filter_type == 0:
                    recon_x = orig_x
                elif filter_type == 1:
                    recon_x = orig_x - orig_a(r, c)
                elif filter_type == 2:
                    recon_x = orig_x - orig_b(r, c)
                elif filter_type == 3:
                    recon_x = orig_x - (orig_a(r, c) + orig_b(r, c)) // 2
                elif filter_type == 4:
                    recon_x = orig_x + self.__paeth_predictor(
                        orig_a(r, c), orig_b(r, c), orig_c(r, c)
                    )
                else:
                    raise NameError(f"filter unknown: {filter_type}")
                Filtered.append(recon_x & 0xFF)
        return Filtered

    def __decompress(self) -> list:
        self.__concatenate_data()
        self.image = zlib.decompress(self.byte_image)
        self.pixel_size = int(
            (len(self.image) / self.chunks[0].info["height"] - 1)
            / self.chunks[0].info["width"]
        )
        if len(self.image) != self.chunks[0].info["height"] * (
            1 + self.chunks[0].info["width"] * self.pixel_size
        ):
            raise ValueError("Image size error")

        stride = self.chunks[0].info["width"] * self.pixel_size
        Recon = []
        recon_a = (
            lambda r, c: Recon[r * stride + c - self.pixel_size]
            if c >= self.pixel_size
            else 0
        )
        recon_b = lambda r, c: Recon[(r - 1) * stride + c] if r > 0 else 0
        recon_c = (
            lambda r, c: Recon[(r - 1) * stride + c - self.pixel_size]
            if r > 0 and c >= self.pixel_size
            else 0
        )

        i = 0
        for r in range(self.chunks[0].info["height"]):
            filter_type = self.image[i]
            i += 1
            for c in range(stride):
                filter_x = self.image[i]
                i += 1
                if filter_type == 0:
                    recon_x = filter_x
                elif filter_type == 1:
                    recon_x = filter_x + recon_a(r, c)
                elif filter_type == 2:
                    recon_x = filter_x + recon_b(r, c)
                elif filter_type == 3:
                    recon_x = filter_x + (recon_a(r, c) + recon_b(r, c)) // 2
                elif filter_type == 4:
                    recon_x = filter_x + self.__paeth_predictor(
                        recon_a(r, c), recon_b(r, c), recon_c(r, c)
                    )
                else:
                    raise NameError(f"filter unknown: {filter_type}")
                Recon.append(recon_x & 0xFF)
        return Recon

    def clear_metadata(self):
        try:
            self.chunks = [c for c in self.chunks if c.type_code in CRITICAL_CHUNKS]
            IDAT = self.__seek("IDAT")
            replacement_IDAT = IDAT[0]
            idx = self.chunks.index(replacement_IDAT)
            self.__concatenate_data()
            self.chunks = [c for c in self.chunks if c.type_code != "IDAT"]
            replacement_IDAT.data_length = len(self.byte_image)
            replacement_IDAT.binary_data = self.byte_image
            replacement_IDAT.info = {"counter": 1}
            replacement_IDAT.CRC = self.__calculate_crc(self.byte_image)
            self.chunks.insert(idx, replacement_IDAT)
        except Exception as err:
            print(type(err), f"{__name__}: {err}")

    def save(self, filename: str = None):
        if filename:
            self.filename = filename
        with open(self.filename, "wb") as f:
            f.write(self.signature)
            for c in self.chunks:
                f.write(c.data_length.to_bytes(4, "big"))
                f.write(c.type_code.encode("utf-8"))
                f.write(c.binary_data)
                f.write(c.CRC)

    def show(self) -> None:
        self.parsed_image = self.__decompress()
        plt.imshow(
            np.array(self.parsed_image).reshape(
                (
                    self.chunks[0].info["height"],
                    self.chunks[0].info["width"],
                    self.pixel_size,
                )
            )
        )
        plt.axis("off")
        plt.show()

    def chunks_info(self) -> dict:
        # sourcery skip: extract-duplicate-method, use-dict-items
        length = 32
        skip = 5
        divide = skip + 10
        horizontal_skip = 3
        for c in self.chunks:
            print("-" * length)
            print(f"{'Chunk type':<{skip+divide}}: {c.type_code}")
            print("-" * length)
            print(f"{'Address':<{skip+divide}}: {c.address}")
            print("-" * length)

            if c.type_code in SUPPORTED_CHUNKS:
                print(f"{'Data:':<{length}}")
                for i in c.info:
                    print(f"{' '*skip}{i:<{divide}}: {c.info[i]}")
            else:
                print("Unsupported chunk.")
            print("-" * length)
            print(f"{'Data length':<{skip+divide}}: {c.data_length}")
            print("-" * length)
            print(f"{'CRC code':<{skip+divide}}: {c.CRC.hex():<15}")
            print("-" * length)
            if c.type_code != "IEND":
                print(end="\n" * horizontal_skip)
