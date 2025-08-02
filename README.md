# 🌿 CoolSpace AI - 智慧冷卻效率優化系統 (純軟體版)

[![Swift](https://img.shields.io/badge/Swift-5.0+-orange.svg)](https://swift.org)
[![ARKit](https://img.shields.io/badge/ARKit-4.0+-green.svg)](https://developer.apple.com/augmented-reality/arkit/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.2+-black.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)

一個創新的純軟體解決方案，利用現代智慧型手機內建的 AR 功能，對室內空間進行 3D 建模與熱點分析，旨在優化住宅與小型商業空間的冷卻效率，顯著降低能源消耗。

## 🎯 核心功能 (MVP & 規劃中)

- **📱 AR 空間掃描**: 使用手機的 ARKit/ARCore 捕捉房間的 3D 幾何結構。
- **☁️ 雲端 AI 分析**: 整合計算流體力學 (CFD) 模擬與機器學習，分析室內氣流。
- **💡 智慧節能建議**: 提供客製化的冷卻優化建議，如調整風扇角度、利用對流等。
- **✅ 零硬體門檻**: 無需購買任何額外硬體，下載 App 即可使用。
- **RESTful API 後端**: 基於 Flask 的後端服務，用於接收與處理 3D 掃描數據。

## 📁 專案架構 (MVP)

這是在 MVP 階段建立的專案結構。

```
CoolSpace AI/
├── 📂 coolspace_app/                # 前端 App (概念驗證)
│   └── ARScannerViewController.swift # 核心 AR 掃描邏輯 (Swift)
│
├── 📂 coolspace_backend/             # 後端服務
│   ├── server.py                     # 主要 Flask 應用程式
│   ├── test_server.py                # 後端單元測試
│   ├── README.md                     # CFD 整合策略文件
│   └── requirements.txt              # Python 依賴套件
│
└── README.md                         # 本專案說明文件
```

## 🚀 快速開始 (後端服務)

目前只有後端服務可以獨立運行以進行測試。

**1. 進入後端目錄**
```bash
cd coolspace_backend
```

**2. 安裝 Python 依賴套件**
```bash
pip install -r requirements.txt
```

**3. 啟動後端開發伺服器**
```bash
python server.py
```
伺服器將在 `http://localhost:5000` 上運行。

## 🌐 存取點

- **後端 API 根目錄**: http://localhost:5000
- **數據上傳端點 (POST)**: http://localhost:5000/api/v1/upload_scan

## 🧪 測試

執行後端服務的單元測試。

```bash
# 從專案根目錄執行
python -m unittest discover coolspace_backend
```

## 🛠️ 技術堆疊 (MVP)

**前端 (概念驗證):**
- Swift, ARKit (for iOS)

**後端:**
- Python 3.9+
- Flask (網頁框架)

**規劃中的技術:**
- **CFD 引擎**: OpenFOAM
- **非同步任務隊列**: Celery, Redis

## 🤝 貢獻

這是一個早期階段的專案，歡迎各種貢獻！

1.  Fork 本專案
2.  建立您的功能分支 (`git checkout -b feature/AmazingFeature`)
3.  提交您的變更 (`git commit -m 'Add some AmazingFeature'`)
4.  推送到分支 (`git push origin feature/AmazingFeature`)
5.  開啟一個 Pull Request

## 📄 授權

本專案採用 MIT 授權條款。

---

**🌿 CoolSpace AI** - 透過智慧與科技，為台灣的永續能源未來賦能。
