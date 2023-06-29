from io import BufferedReader


CRITICAL_CHUNKS = {"IHDR", "PLTE", "IDAT", "IEND"}
SUPPORTED_CHUNKS = CRITICAL_CHUNKS.union({"cHRM", "pHYs", "hIST", "gAMA","sBIT"})
"""
Take into consideration possibility of no inheritance and calling specific chunks in Chunk __init__
"""


def IHDR(data: bytes):
    try:
        info = dict(
            zip(
                ("bit_depth", "color_type", "compression", "filter", "interlace"),
                data[8:14],
            )
        )
        info["width"] = int.from_bytes(data[:4], "big")
        info["height"] = int.from_bytes(data[4:8], "big")
        if info["width"] == 0 or info["height"] == 0:
            # or self.width > 2**31 or self.height > 2**31:
            raise ValueError("Resolution")
        if info["bit_depth"] not in (1, 2, 4, 8, 16):  # 6???
            raise ValueError("Bit depth")
        if info["color_type"] not in (0, 2, 3, 4, 6):
            raise ValueError("Color type")
    except ValueError as err:
        print(type(err), f"{__name__}: {err}")
    finally:
        return info
    
def PLTE(data: bytes):
    try:
        if len(data) % 3:
            raise IndexError("Palette entries")
        palette = [(data[i], data[i+1], data[i+2]) for i in range(0, len(data), 3)]
        info = { 
            "palette": palette,
        }
    except IndexError as err:
        print(type(err), f"{__name__}: {err}")
        info = {}
    finally:
        return info





def cHRM(data: bytes):
    try:
        info = dict(
            zip(
                (
                    "white_point_x",
                    "white_point_y",
                    "red_x",
                    "red_y",
                    "green_x",
                    "green_y",
                    "blue_x",
                    "blue_y",
                ),
                [
                    int.from_bytes(data[b : b + 4], "big")
                    for b in range(0, len(data), 4)
                ],
            )
        )
    except IndexError as err:
        print(type(err), f"{__name__}: {err}")
    finally:
        return info


def pHYs(data: bytes):
    try:
        info = {
            "px_x_axis": int.from_bytes(data[:4], "big"),
            "px_y_axis": int.from_bytes(data[4:8], "big"),
            "unit_specifier": data[8],
        }
        if info["unit_specifier"] not in {0, 1}:
            raise ValueError("Unit specifier")
    except IndexError as err:
        print(type(err), f"{__name__}: {err}")
    finally:
        return info
    
def hIST(data: bytes):
    try:
        histogram = []
        for i in range(0, len(data), 2):
            count = int.from_bytes(data[i : i + 2], "big")
            histogram.append(count)
        info = {"histogram": histogram}
    except Exception as err:
        print(type(err), f"{__name__}: {err}")
    finally:
        print(histogram)
    
        return info

def gAMA(data: bytes):
    try:
        gamma = int.from_bytes(data, "big") / 100000
        info = {"gamma": gamma}
    except Exception as err:
        print(type(err), f"{__name__}: {err}")
    finally:
        return info
def sBIT(data: bytes):
    try:
        if len(data) == 1:
            grayscale_bits = data[0]
            info = {"grayscale_bits": grayscale_bits}
        elif len(data) == 3:
            red_bits, green_bits, blue_bits = data
            info = {
                "red_bits": red_bits,
                "green_bits": green_bits,
                "blue_bits": blue_bits
            }
        else:
            raise ValueError("Invalid sBIT data")
    except Exception as err:
        print(type(err), f"{__name__}: {err}")
    finally:
        return info


class Chunk(object):
    def __init__(self, stream: BufferedReader) -> None:
        self.data_length = int.from_bytes(stream.read(4), "big")
        if self.data_length > 2**31:
            raise ValueError("Chunk bytes length exceeded")
        self.type_code = stream.read(4).decode("utf-8")
        self.binary_data = stream.read(self.data_length)
        try:
            self.info = eval(self.type_code)(self.binary_data)
        except Exception:
            self.info = {}
        self.CRC = stream.read(4)

