# Ceiba 備份下載軟體 Ceiba Downloader

> 本程式仍在開發中，雖然目前可以正常使用，但若不急的話建議寒假再來使用，功能上會更完整。另外歡迎任何的 issue/pull request，也歡迎 star 本專案與開啟 notification 以收到最新消息。

![](https://i.imgur.com/TVY3uUD.gif)

## 安裝


你可以選擇以下兩種方式安裝：

### 1. 執行 exe

> 目前 Releases 只支援 Windows。Linux/Mac 使用者請先選擇第二種方式或等到我更新 Linux/Mac 的 Installer。

請在 [Releases](https://github.com/jameshwc/Ceiba-Downloader/releases) 頁面找到 `ceiba-downloader.exe` 進行下載。

> 目前用 PyInstaller 打包的程式可能會被 Windows Defender 當作病毒，可以在 Windows Defender 裡面設定排除該程式；若不放心，可以請懂 Python 的朋友直接執行程式碼（參考以下）。

### 2. 執行程式碼

若不想下載打包好的 exe，可以用 python 執行程式碼。

0. 推薦建立虛擬環境 (virtualenv, pyenv, etc.)
1. python 使用 3.9+ 版本（配合 PySide6）
2. `pip3 install -r requirements.txt`
3. `python3 gui_main.py`