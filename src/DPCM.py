import cv2
import numpy as np
import os
import Tool
import time

root = os.path.join(os.path.dirname(os.path.dirname(__file__)))
data = os.path.join(root, "data/")

quantizer = {
    "1_bit": {
        "bits": 1,
        "number_of_level": 2,
        "bound": [0],
        "level": [-10, 10],
    },
    "2_bit": {
        "bits": 2,
        "number_of_level": 4,
        "bound": [-8, 0, 8],
        "level": [-14, -4, 4, 14],
    },
    "3_bit": {
        "bits": 3,
        "number_of_level": 8,
        "bound": [-16, -8, -3, 0, 3, 8, 16],
        "level": [-24, -11, -5, -1, 1, 5, 11, 24],
    },
    "3_bit_wide": {
        "bits": 3,
        "number_of_level": 8,
        "bound": [-32, -16, -6, 0, 6, 16, 32],
        "level": [-48, -24, -10, -3, 3, 10, 24, 48],
    },
}


def quantize(e, bound, level):
    idx = int(np.searchsorted(bound, e, side="right"))
    q = level[idx]
    return idx, q


def dpcm_encode(gray_img, bound, level):
    img = gray_img.astype(np.float64)
    H, W = img.shape

    first_pixel = img[:, 0].astype(np.uint8)
    quantized = np.zeros((H, W - 1), dtype=np.uint8)

    for y in range(H):
        predict = float(first_pixel[y])
        for x in range(1, W):
            e = img[y, x] - predict
            idx, q = quantize(e, bound, level)
            quantized[y, x - 1] = idx
            predict += q

    return first_pixel, quantized


def dpcm_decode(first_pixel, quantized, level):
    H = first_pixel.shape[0]
    W = quantized.shape[1] + 1

    img = np.zeros((H, W), dtype=np.float64)

    for y in range(H):
        predict = first_pixel[y]
        img[y, 0] = predict
        for x in range(1, W):
            predict += float(level[quantized[y, x - 1]])
            img[y, x] = predict

    return np.clip(np.round(img), 0, 255).astype(np.uint8)


if __name__ == "__main__":
    gray = cv2.imread(os.path.join(data, "lena_gray.png"), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise FileNotFoundError("something wrong")
    for name, config in quantizer.items():
        t_encode = 0.0
        t_decode = 0.0

        for i in range(5):
            t0 = time.perf_counter()
            fp, quantized = dpcm_encode(gray, config["bound"], config["level"])
            t_encode += time.perf_counter() - t0

            t0 = time.perf_counter()
            return_img = dpcm_decode(fp, quantized, config["level"])
            t_decode += time.perf_counter() - t0

        fp, quantized = dpcm_encode(gray, config["bound"], config["level"])
        return_img = dpcm_decode(fp, quantized, config["level"])

        out_path = os.path.join(data, f"lena_dpcm_{name}.png")
        cv2.imwrite(out_path, return_img)

        m = Tool.mse(gray, return_img)
        p = Tool.psnr(m)
        c = Tool.cr(gray.shape[0], gray.shape[1], config["bits"], config["number_of_level"])
        t_encode /= 5.0
        t_decode /= 5.0

        print(
            f"name:{name}, mse:{m:.2f}, psnr:{p:.2f}, cr:{c:.2f}, t_encode:{t_encode:.2f}. t_decode:{t_decode:.2f}, shape:{gray.shape}"
        )
