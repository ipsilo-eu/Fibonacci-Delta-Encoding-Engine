"""
FDEE - Fibonacci Delta Encoding Engine
(c) 2025 Tudor Simion tudor@ipsilo.eu | ALL RIGHTS RESERVED

PURPOSE: Positive integer compression via the 'Index ± Offset' method.
BEST RESULTS WHEN NUMBERS ARE CLOSE TO FIBONACCI numbers
"""

"""
The print() functions have been commented out for professional reasons. 

This code isn't usually meant to be used as standalone for files, so an engineer can easily integrate it 
inside their software(with the appropriate license, of course) or be requested consultancy from the author 
via email at tudor@ipsilo.eu . 
"""

import os
from bisect import bisect_left

class FibonacciEngine:
    def __init__(self):
        self.numbers = [0, 1]
        for i in range(2, 93): # TO BE MODIFIED to the largest Fibonacci reference number expected!!! 93 is just for reference
            self.numbers.append(self.numbers[-1] + self.numbers[-2])

    def textTransform(self, n):
        out = bytearray()
        while n >= 0x80:
            out.append((n & 0x7f) | 0x80)
            n >>= 7
        out.append(n)
        return out

    def hexTransform(self, stream):
        res, shift = 0, 0
        while True:
            b = stream.read(1)
            if not b: return None
            b = b[0]
            res |= (b & 0x7f) << shift
            if not (b & 0x80): break
            shift += 7
        return res

    def encode(self, n):
        pos = bisect_left(self.numbers, n)
        if pos == 0: idx = 0
        elif pos == len(self.numbers): idx = len(self.numbers) - 1
        else:
            before, after = self.numbers[pos-1], self.numbers[pos]
            idx = pos if (after - n) < (n - before) else pos - 1
        
        pillar_val = self.numbers[idx]
        if n == pillar_val:
            return self.textTransform((idx << 2) | 0)
        
        op = 1 if n > pillar_val else 2
        offset = abs(n - pillar_val)
        return self.textTransform((idx << 2) | op) + self.textTransform(offset)

    def decode(self, stream):
        header = self.hexTransform(stream)
        if header is None: return None
        op = header & 0x03
        idx = header >> 2
        base = self.numbers[idx]
        if op == 0: return base
        offset = self.hexTransform(stream)
        if offset is None: return None
        return base + offset if op == 1 else base - offset

    def compress_file(self, input_txt, output_bin):
        # print(f"[*] Compressing {input_txt}...")
        with open(input_txt, 'r', encoding='utf-8') as f_in:
            with open(output_bin, 'wb') as f_out:
                for line in f_in:
                    for part in line.split(" "): #integer separation
                        try:
                            f_out.write(self.encode(int(part)))
                        except ValueError:
                            continue
                f_out.flush()
                os.fsync(f_out.fileno()) 
        # print(f"Binary size: {os.path.getsize(output_bin)} bytes.")

    def decompress_file(self, input_bin, output_txt):
        # print(f"[*] Decompressing {input_bin}...")
        results = []
        with open(input_bin, 'rb') as f_in:
            while True:
                val = self.decode(f_in)
                if val is None: break
                results.append(str(val))
        
        with open(output_txt, 'w', encoding='utf-8') as f_out:
            f_out.write(" ".join(results)) #integer separation
            f_out.flush()
        # print(f"Reconstructed: {output_txt}")


# Standalone usage:
"""
if __name__ == "__main__":

    engine = FibonacciEngine()

    # File Operations:
    engine.compress_file("data.txt", "data.bin") 
    engine.decompress_file("data.bin", "data_restored.txt")

    # Integration Examples:
    encoded_bytes = engine.encode(12345)
    decoded_value = engine.decode(io.BytesIO(encoded_bytes))
"""

