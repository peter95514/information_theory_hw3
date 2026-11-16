import cv2
import numpy as np
import os

root = os.path.join(os.path.dirname(os.path.dirname(__file__)))
data = os.path.join(root, "data/")

quantizer = {
    "2-bit": {
        "bits": 2,
        "bound": [-8, 0, 8],
        "level": [-12, -4, 4, 12],
    },
    "2-bit": {
        "bits": 2,
        "bound": [-8, 0, 8],
        "level": [-12, -4, 4, 12],
    },
    "2-bit": {
        "bits": 2,
        "bound": [-8, 0, 8],
        "level": [-12, -4, 4, 12],
    },
    "2-bit": {
        "bits": 2,
        "bound": [-8, 0, 8],
        "level": [-12, -4, 4, 12],
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
        fp, quantized = dpcm_encode(gray, config["bound"], config["level"])
        img_decode = dpcm_decode(fp, quantized, config["level"])
        out_path = os.path.join(data, "dpcm/", f"lena_dpcm_{name}.png")
        cv2.imwrite(out_path, img_decode)
