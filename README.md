# (Archived) Ceiba 備份下載軟體 Ceiba Downloader
[![No Maintenance Intended](http://unmaintained.tech/badge.svg)](http://unmaintained.tech/)[![GitHub stars](https://img.shields.io/github/stars/jameshwc/Ceiba-Downloader)](https://github.com/jameshwc/Ceiba-Downloader/stargazers) ![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/jameshwc/Ceiba-Downloader?sort=semver) ![GitHub all releases](https://img.shields.io/github/downloads/jameshwc/Ceiba-Downloader/total) [![wakatime](https://wakatime.com/badge/user/2e96fba1-4706-4851-b24f-13b1d9f5e5e0/project/b4b2c09f-879d-4d9d-8815-90aa4c171ce0.svg)](https://wakatime.com/badge/user/2e96fba1-4706-4851-b24f-13b1d9f5e5e0/project/b4b2c09f-879d-4d9d-8815-90aa4c171ce0) [![GitHub license](https://img.shields.io/github/license/jameshwc/Ceiba-Downloader)](https://github.com/jameshwc/Ceiba-Downloader/blob/master/LICENSE) 

## Archive Notice 封存

As of 2024 Jan, this project has been archived and is no longer actively maintained or supported due to the shutdown of the NTU Ceiba site. 

由於 Ceiba 已在 2024 年初下線，本軟體功成身退，將不再執行任何維護與更新。

---

[README in English](https://github.com/jameshwc/Ceiba-Downloader/blob/master/README-en.md)

![](https://i.imgur.com/z7bqTNs.gif)

## 安裝

你可以選擇以下兩種方式安裝：

### 1. 下載執行檔 （推薦，適用一般使用者）

請在 [Releases](https://github.com/jameshwc/Ceiba-Downloader/releases/latest) 頁面找到屬於自己作業系統的 `ceiba-downloader.zip` 進行下載。

解壓縮後，在 `ceiba-downloader` 資料夾中找到 `ceiba-downloader` (Windows 為 `ceiba-downloader.exe`) 並執行。

### 2. 執行程式碼（需會使用 Python）

若不想下載打包好的執行檔，可以用 python 執行程式碼。

0. 推薦建立虛擬環境 (`virtualenv`, `pyenv`, etc.)
1. `python` 使用 `3.7+` 版本（`mac` 需要 `3.9+` 版本，理由未知）
2. `pip3 install -r requirements.txt`
3. `python3 gui_main.py`

## 已知問題

- Windows 7/8/8.1 可能無法正常運作
