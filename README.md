# ADM / DPCM 壓縮實作

## 作業說明

本次作業分為ADM以及DPCM兩個部分，關於實驗要使用的輸入圖以在wiki下載的彩色原圖並以`ChangeToGray.py`處理成灰階圖片，
以便後續實驗使用。若要重現實驗，可以分別在ADM.py,DPCM.py兩個檔案的開始找到設定的區塊，只要修改名字及參數並執行，輸出圖片會存在data資料夾中

## ADM壓縮

ADM壓縮的原始碼可以在`src/ADM.py`裡面查看，參數按照作業要求為(Δ[0], Δmin) = (2,1)、(4,1)、(8,1)、(8,2)

### ADM壓縮算法說明

1. 處理流程

    依作業要求採逐列光柵掃描（每列由左至右、列與列由上至下）。每一列都獨立處理，開頭重新初始化預測器。
初始條件（每列開始時）：

| 變數 | 初始值 |
| --- | --- |
| `predict` | `img[y, 0]`|
| `delta` | Δ[0] |
| `prev_e` | +1 |
2. 編碼(encode)

    對該列第 x = 1 … W−1 個像素:

    1. 計算`e`：`e = img[y,x] − predict`
        - `e ≥ 0` → 輸出 bit 1，令 `e = +1`
        - `e < 0` → 輸出 bit 0，令 `e = −1`
        - 誤差相等判定：誤差剛好為 0 時視為正（輸出 1）
    2. 更新`delta`：
        - 若 `|delta| ≥ Δmin`：`delta = |delta| × (e + 0.5 × prev_e)`
        - 否則：`delta = Δmin × e`
    3. 更新`predict`：`predict = predict + delta`
    4. 記錄`e`：`prev_e = e`
3. 解碼(decode)

    解碼端的出使條件與編碼端完全相同，流程則如下:

    1. 初始化`predict = first_pixel[y]`，`delta = Δ[0]`，`prev_e = +1`
    2. 讀取 bit：`1 → e = +1`，`0 → e = −1`
    3. 以相同公式更新 `delta`，再 `predict += delta`，輸出 `img[y,x] = predict`
    4. `prev_e = e`

### 不同參數的分析

- slope overload
    - 發生位置:快速變換處
    - 視覺表現:邊緣模糊
- granular noise
    - 發生位置:平坦或是緩變區域
    - 視覺表現:平坦區出現細小顆粒雜訊

四組參數分析

- (2,1)

    ![](data/lena_adm_2_1.png)

- (4,1)

    ![](data/lena_adm_4_1.png)

- (8,1)

    ![](data/lena_adm_8_1.png)

- (8,2)

    ![](data/lena_adm_8_2.png)

- granular noise

    - 前三組參數表現差不多因為其`delta_min`皆為1，而最後一組參數則因`delta_min`的上升而有較明顯的表現

- slope overload

    - 前三組參數表顯會較為明顯因為其`delta_min`較低，而最後一組的表現則會有所改善

## DPCM壓縮

1. 處理流程

    同樣採逐列光柵掃描，每一列獨立處理。以前一個「重建像素」作為當前像素的預測值。
2. 量化器

    量化器由兩個陣列定義：
    - `level`：重建值，共 L = 2^bits 個
    - `bound`：決策邊界，共 L−1 個，遞增排列
    量化規則以`np.searchsorted(bound, e, side="right")`找出對應的區間，相等時則歸入較大的那一區間

3. 編碼(encode):
    對每一列的第`x = 1 ... W - 1`個像素
    - 計算預測誤差:`e = img[y,x] - predict`
    - 套用前面提到的量化規則找到`q`並存`idx`
    - 更新`predict += q`

4. 解碼(decode):

    - 初始化 `predict = first_pixel[y]`
    - 讀取索引 idx，查表得 `q = level[idx]`
    - `predict += q`，輸出 `img[y,x] = predict`
    最後將`img`做`round`及`clip`到[0,255]後才進行輸出
5. 量化器參數選擇
    |名稱	|bits	|bound	|level|
    |---|---|---|---|
    |1_bit|	1|	[0]|	[−10, 10]|
    |2_bit|	2|	[−8, 0, 8]|	[−14, −4, 4, 14]|
    |3_bit|	3|	[−16, −8, −3, 0, 3, 8, 16]|	[−24, −11, −5, −1, 1, 5, 11, 24]|
    |3_bit_wide|	3	|[−32, −16, −6, 0, 6, 16, 32]|	[−48, −24, −10, −3, 3, 10, 24, 48]|

    - 前三組主要是想要比對bit數量多寡對壓縮的影響
    - 後兩組的目的是想要比對在bit數量一樣的情況下範圍對壓縮的影響

## 品質評估與實驗分析

這個環節會用MSE,PSNR,CR,Tencode/Tdecode四個指標來比較兩種壓縮在四種指標下的表現，另外，這邊CR的評估是以理論上所需的編碼位元數進行運算

### ADM
