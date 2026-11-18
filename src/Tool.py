import numpy as np


def mse(original, reconstructed):
    diff = original.astype(np.float64) - reconstructed.astype(np.float64)
    return float(np.mean(diff**2))


def psnr(mse_value):
    if mse_value == 0:
        return float("inf")
    return 10 * np.log10(255.0**2 / mse_value)


def cr(H, W, bit, extra_bits):
    original = H * W * 8
    encode = H * 8 + H * (W - 1) * bit + extra_bits
    return original / encode
