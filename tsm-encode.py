import math
import textwrap
import sys
import os

try:
    import numpy as np

except ImportError:
    os.system("py -m pip install numpy")
    import numpy as np

try:
    from PIL import Image

except ImportError:
    os.system("py -m pip install pillow")
    from PIL import Image

def pad_reshape(array: np.ndarray[int], n: int, m: int) -> np.ndarray[np.ndarray[int]]:
    extra = n*m - len(array)
    new_array = np.pad(array, [(0, extra)])
    new_array.resize((n, m))
    return new_array

filename = sys.argv[1]
filetype = os.path.splitext(filename)[-1][1:].encode("utf-8")

with open(filename, "rb") as file:
    data = bytearray(file.read())

temp = len(data).to_bytes(2, "big")
temp += len(filetype).to_bytes()
temp += filetype
print(temp)
data = temp + data

packed = []

checksum = 0

for i in data:
    checksum += i
    checksum %= 0xFFFF

data += checksum.to_bytes(2, "big")

for i in data:
    byte = textwrap.wrap(bin(i)[2:].zfill(8), 2)

    for b in byte:
        packed.append(int(b, base=2))

image_size = math.ceil(math.sqrt(len(data) * 4))
image_scale = 20

print(image_size * image_size, len(data) * 4)

colors = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 0, 255),
    (255, 255, 255)
]

def get_color(color):
    return colors[color]

print(packed)

array_data = np.array(packed)
array_data = pad_reshape(array_data, image_size, image_size)
array_data = np.fliplr(array_data)
array_data = np.rot90(array_data)

print(array_data)

canvas = Image.new("RGB", (image_size, image_size))

for y in range(array_data.shape[1]):
    for x in range(array_data.shape[0]):
        color = get_color(array_data[x, y])
        canvas.putpixel((x, y), color)
        # print(bin(array_data[x, y])[2:].zfill(2), end=" ")

canvas = canvas.resize((image_size * image_scale, image_size * image_scale), Image.Resampling.NEAREST)
canvas.save(sys.argv[2])