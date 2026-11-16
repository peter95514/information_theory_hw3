# ADM / DPCM 壓縮實作

## 作業說明

本次作業分為ADM以及DPCM兩個部分，關於實驗要使用的輸入圖以在wiki下載的彩色原圖並以`ChangeToGray.py`處理成灰階圖片，
以便後續實驗使用

## ADM壓縮

ADM壓縮的原始碼可以在`src/ADM.py`裡面查看，參數按照作業要求為(Δ[0], Δmin) = (2,1)、(4,1)、(8,1)、(8,2)

### ADM壓縮算法說明

ADM壓縮分為encode,decode兩個部分encode更新邏輯參考上課投影片的內容
