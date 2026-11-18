# ADM / DPCM 壓縮實作

## 作業說明

本次作業分為ADM以及DPCM兩個部分，關於實驗要使用的輸入圖以在wiki下載的彩色原圖並以`ChangeToGray.py`處理成灰階圖片，
以便後續實驗使用。若要重現實驗，可以分別在`ADM.py`,`DPCM.py`兩個檔案的開始找到設定的區塊，只要修改名字及參數並執行，輸出圖片會存在data資料夾中

- lena原圖

    ![](data/lena.png)

- lena灰階圖

    ![](data/lena_gray.png)

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

    - 1_bit

        ![](data/lena_dpcm_1_bit.png)
    - 2_bit

        ![](data/lena_dpcm_2_bit.png)
    - 3_bit

        ![](data/lena_dpcm_3_bit.png)
    - 3_bit_wide

        ![](data/lena_dpcm_3_bit_wide.png)

## 品質評估與實驗分析

這個環節會用MSE,PSNR,CR,Tencode/Tdecode四個指標來比較兩種壓縮在四種指標下的表現，另外，這邊CR的評估是以理論上所需的編碼位元數進行運算

|指標	|定義|
| --- | ---|
|MSE|	灰階原圖與重建圖逐像素差的平方平均（皆轉為 float64 計算，避免 uint8 溢位）|
|PSNR|	10·log10(255² / MSE) dB，MSE = 0 時記為 ∞|
|CR|	原始總位元數 / 總編碼位元數|
|Tencode / Tdecode|各重複 5 次，以 time.perf_counter() 取平均|
### ADM結果
 | (Δ[0], Δmin)	| MSE	| PSNR (dB)	| CR	| Tencode (s)	| Tdecode (s)|
 | --- | --- | --- | --- | --- | --- |
 | (2, 1)	| 356.74	| 22.61	| 7.89	| 0.0619	| 0.0481|
 | (4, 1)	| 349.83| 22.69	| 7.89	| 0.0560	| 0.0478|
 | (8, 1)	| 352.51| 22.66	| 7.89	| 0.0565	| 0.0481|
 | (8, 2)	| 319.76| 23.08	| 7.89	| 0.0580	| 0.0486|

 - Δ[0] 影響很小。(2,1)、(4,1)、(8,1) 的 MSE 只差約 7（349.83～356.74），原因是Δ[0] 只影響每列開頭的幾個像素
 - Δmin 影響較大。 (8,2) 的 MSE 為 319.76，比 Δmin = 1 的三組低約 30，PSNR 高約 0.4 dB。
 - CR 與時間： ADM 每像素固定 1 bit，四組 CR 相同；時間差異屬於量測誤差範圍。
### DPCM結果
 | 量化器	| MSE	| PSNR (dB)	| CR	| Tencode (s)	| Tdecode (s)|
 | --- | --- | --- | --- | --- | --- |
 | 1_bit	| 310.56	| 23.21	| 7.89	| 0.4423	| 0.0389|
 | 2_bit	| 173.11	| 25.75	| 3.98	| 0.4524| 0.0386|
 | 3_bit	| 62.09	| 30.20	| 2.66	| 0.4828	| 0.0390|
 | 3_bit_wide	| 14.49	| 36.52	| 2.66	| 0.4817	| 0.0383|

 - bits 數的影響： 從 1 → 2 → 3 bits，PSNR 由 23.21 升到 25.75 再到 30.20 dB，代價是 CR 由 7.89 降到 3.98 再到 2.66
 - 3_bit 與 3_bit_wide（位元數相同，範圍不同）： 3_bit_wide 的 MSE（14.49）遠低於 3_bit（62.09），PSNR 高出 6.3 dB，CR 相同，所以在這張影像上 3_bit_wide 明顯較好。

### ADM, DPCM比較

- CR 與品質： DPCM 提高 bits 或擴大量化範圍可大幅提升 PSNR（最高 36.52 dB），代價是 CR 降到 2.66。
- 執行時間：雖然兩者的複雜度相同(`O(H*W)`)，但DPCM的encode會不斷呼叫`np.searchsorted`，因此encode會比ADM花費更多時間
