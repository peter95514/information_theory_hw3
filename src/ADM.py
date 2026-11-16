import cv2
import numpy as np
import os

root = os.path.join(os.path.dirname(os.path.dirname(__file__)))
data = os.path.join(root, "data/")

config = {
    "2_1": {
        "delta_0": 2,
        "delta_min": 1,
    },
    "4_1": {
        "delta_0": 4,
        "delta_min": 1,
    },
    "8_1": {
        "delta_0": 8,
        "delta_min": 1,
    },
    "8_2": {
        "delta_0": 8,
        "delta_min": 2,
    },
}


def adm_encode(gray_img, delta_0, delta_min):
    img = gray_img.astype(np.float64)
    H, W = img.shape

    first_pixel = img[:, 0].astype(np.uint8)
    bitstream = np.zeros((H, W - 1), dtype=np.uint8)

    for y in range(H):
        delta = float(delta_0)
        prev_e = 1.0
        predict = float(first_pixel[y])
        for x in range(1, W):
            e = img[y, x] - predict
            if e >= 0:
                e = 1.0
                bitstream[y, x - 1] = 1
            else:
                e = -1.0
                bitstream[y, x - 1] = 0

            if prev_e != None:
                delta_tmp = abs(delta)
                if delta_tmp >= delta_min:
                    delta = delta_tmp * (e + prev_e / 2.0)
                else:
                    delta = float(delta_min) * e
            predict = predict + delta
            prev_e = e

    return first_pixel, bitstream


def adm_decode(first_pixel, bitstream, delta_0, delta_min):
    H = first_pixel.shape[0]
    W = bitstream.shape[1] + 1
    img = np.zeros((H, W), dtype=np.float64)

    for y in range(H):
        delta = float(delta_0)
        prev_e = 1.0
        predict = float(first_pixel[y])
        img[y, 0] = predict
        for x in range(1, W):
            e = 0
            if bitstream[y, x - 1] == 1:
                e = 1.0
            else:
                e = -1.0

            delta_tmp = abs(delta)

            if delta_tmp >= delta_min:
                delta = delta_tmp * (e + prev_e / 2)
            else:
                delta = float(delta_min) * e

            predict = predict + delta
            img[y, x] = predict
            prev_e = e
    return np.clip(np.round(img), 0, 255).astype(np.uint8)


if __name__ == "__main__":
    img = os.path.join(data, "lena_gray.png")
    gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise FileNotFoundError("something wrong")
    for name, cfg in config.items():
        fp, bits = adm_encode(gray, cfg["delta_0"], cfg["delta_min"])
        return_img = adm_decode(fp, bits, cfg["delta_0"], cfg["delta_min"])
        out_path = os.path.join(data, f"lena_adm_{name}.png")
        cv2.imwrite(out_path, return_img)
