from PIL import Image
import textwrap
import sys

filename = sys.argv[1]

data = []

file = Image.open(filename).convert("RGB")
data_size = file.size[0] // 20

file = file.resize((data_size, data_size), Image.Resampling.NEAREST)

data = file.getdata()

colors = ( (0, 0, 0, "BL"),
            (255, 0, 0, "R"),
            (0, 0, 255, "B"),
            (255, 255, 255, "W") )


def nearest_colors( subjects, query ):
    return min( subjects, key = lambda subject: sum( (s - q) ** 2 for s, q in zip( subject, query ) ) )

def get_pattern(color):
    color = nearest_colors(colors, color)[-1]

    if color == "BL": return 0
    if color == "R": return 1
    if color == "B": return 2
    if color == "W": return 3

    raise ValueError(f"lmao: {color}")

decoded = ""

for i in data:
    decoded += bin(get_pattern(i))[2:].zfill(2)

decoded = textwrap.wrap(decoded, 8)

if len(decoded[-1]) < 8:
    decoded = decoded[:-1]

def get_int(data):
    byte = int(data[0], base=2)
    byte <<= 8
    byte += int(data[1], base=2)
    return byte

def to_str(data):
    string = ""

    for i in data:
        string += chr(int(i, base=2))
    
    return string

original_data = decoded

print(original_data)

length = get_int(decoded[0:2])
ft_length = int(decoded[2], base=2)
filetype = to_str(decoded[3:3 + ft_length])
offset = 3 + ft_length

data = decoded[offset:length + offset]
checksum = get_int(decoded[length + offset:])

print(length, data, checksum)

my_checksum = 0

for i in decoded[:length + offset]:
    my_checksum += int(i, base=2)
    my_checksum %= 0xFFFF

if my_checksum != checksum:
    raise ValueError(f"Read error: checksum mismatch (Original: {checksum}, yours: {my_checksum})")

print(checksum, my_checksum)

print(filetype)

full_data = bytearray()

for i in data:
    char = int(i, base=2)
    full_data += char.to_bytes()

with open(f"{sys.argv[2]}.{filetype}", "wb") as file:
    file.write(full_data)