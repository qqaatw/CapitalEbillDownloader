# 群益電子對帳單下載器 Capital Ebill Downloader

## 簡介 Description

此下載器能依照你所選擇的日期區間下載電子對帳單，並轉存為excel格式供後續分析使用。 

This downloader downloads ebills according to the selected date range and converts to excel format for subsequent analyses.

## 安裝 Installation

    # 下載本專案 Clone Repository
    git clone https://github.com/qqaatw/CapitalEbillDownloader.git
    
    # 安裝相關套件 Install required packages (Tested in python 3.7)
    pip install -r requirements.txt

## 使用方法 Usage

1. 取得簽章憑證
    1. 開啟Chrome/Edge，並確認此瀏覽器已申請過憑證
    
    2. 進入 https://www.capital.com.tw/Service2/account/membill/ebillDefault.asp 進行登入

    3. 按F12開啟開發人員選項，選擇Application頁籤，點擊左側Local Storage之 https://www.capital.com.tw

    4. 找到TWCA開頭的項目，並複製Value中的b64P12Cert值

2. 開啟config.json填入組態資訊

3. 啟動程式，並依照畫面指示操作

        python main.py

## 注意事項 Note

- 由於需要顯示圖片驗證碼，請在有GUI的環境下執行程式，例如Windows。(未來也許會加入自動辨識驗證碼)
- 若無可選擇的日期，可能是帳號、密碼、圖片驗證碼或憑證字串輸入錯誤。
- 所有簽章動作皆在本機進行，無憑證外洩疑慮，詳情請參閱sign_ca.py。
- 使用上如有遇到任何問題，請發issue告知，將會盡快回覆。

## 授權條款 License

本程式採 Apache License 2.0 條款釋出