# Ceiba 備份下載軟體 Ceiba Downloader

> 歡迎任何的 issue/pull request，或 star 本專案與開啟 notification 以收到最新消息。

![](https://i.imgur.com/z7bqTNs.gif)

## 安裝


你可以選擇以下兩種方式安裝：

### 1. 執行 exe

請在 [Releases](https://github.com/jameshwc/Ceiba-Downloader/releases) 頁面找到屬於自己作業系統的 `ceiba-downloader.zip` 進行下載。

解壓縮後，在 `ceiba-downloader` 資料夾中找到 `ceiba-downloader` (Windows 為 `ceiba-downloader.exe`) 並執行。

### 2. 執行程式碼

若不想下載打包好的 exe，可以用 python 執行程式碼。

0. 推薦建立虛擬環境 (virtualenv, pyenv, etc.)
1. python 使用 3.9+ 版本（配合 PySide6）
2. `pip3 install -r requirements.txt`
3. `python3 gui_main.py`