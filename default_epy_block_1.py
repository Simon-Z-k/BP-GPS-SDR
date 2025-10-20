"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

class blk(gr.sync_block):  # <-- sync_block = jednodušší forma
    def __init__(self, sat_id=1, sample_rate=1023000):
        gr.sync_block.__init__(self,
            name="C/A code generator",
            in_sig=None,
            out_sig=[np.int16])  

        self.sat_id = sat_id
        self.sample_rate = sample_rate
        self.code = self.generate_ca_code(sat_id)
        self.index = 0

    def generate_ca_code(self, sat_id):
        G1 = np.ones(10, dtype=int)
        G2 = np.ones(10, dtype=int)
        ca = np.zeros(1023, dtype=int)

        # Tabulka PRN fází podle IS-GPS-200
        tap_table = {
            1: (2, 6), 2: (3, 7), 3: (4, 8), 4: (5, 9),
            5: (1, 9), 6: (2, 10), 7: (1, 8), 8: (2, 9),
            9: (3, 10), 10: (2, 3)
        }
        tap = tap_table.get(sat_id, (2, 6))

        for i in range(1023):
            g1_out = G1[-1]
            g2_out = (G2[tap[0]-1] ^ G2[tap[1]-1]) % 2
            ca[i] = g1_out ^ g2_out

            # feedback
            G1_fb = (G1[2] ^ G1[9]) % 2
            G2_fb = (G2[1] ^ G2[2] ^ G2[5] ^ G2[7] ^ G2[8] ^ G2[9]) % 2

            G1[1:] = G1[:-1]
            G2[1:] = G2[:-1]
            G1[0] = G1_fb
            G2[0] = G2_fb

        # přepočet {0,1} -> {-1,+1}
        return (1 - 2*ca).astype(np.int16)

    def work(self, input_items, output_items):
        out = output_items[0]
        for i in range(len(out)):
            out[i] = self.code[self.index]
            self.index = (self.index + 1) % len(self.code)
        return len(out)
