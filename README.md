# 🤖 PersonaLlama-3: Heterogeneous Multi-Persona Fine-tuning

本專案基於 **Llama-3-8B** 模型，利用 **Unsloth 4-bit LoRA** 技術，在單張消費級顯卡上實現了異質語料的多重人格微調。模型具備在 **[NLP 技術助教]**、**[感性感情導師]** 與 **[極品感情嘴替]** 三種極端風格間切換的能力。

## 🚀 專案特點
- **高效能微調**：採用 Unsloth 框架，微調速度提升 2x，顯存佔用降低 70%，使 8B 模型能在 12GB VRAM 環境下流暢訓練。
- **權重平衡策略**：針對數據量極度不均（NLP 技術數據 vs. 社交感性語料）的情況，採用 **3x 動態過取樣 (Oversampling)** 成功保留了基礎模型的邏輯推理與專業知識。
- **除錯與優化歷程**：詳細記錄模型從「模板塌陷」到「穩定生成」的技術迭代。

## 💻 硬體環境與負載
- **GPU**: NVIDIA GeForce RTX 3080 Ti (12GB VRAM)
- **Peak Power Draw**: 訓練期間最高功耗達 **391W**
- **Memory Usage**: 穩定佔用約 11.2GB / 12GB (量化微調優勢)
- **OS**: Ubuntu 22.04 (via WSL2)

## 📊 訓練迭代分析 (Version 1.0 vs 2.0)

為了解決過擬合問題，本實驗經歷了兩次核心改進：

| 參數 | Version 1.0 (Overfitted) | Version 2.0 (Optimized) |
| :--- | :--- | :--- |
| **Epochs** | 10 | 3 |
| **Data Quality** | 原始 PTT/Dcard 混合雜訊 | 經 Regex 二次清洗之純淨語料 |
| **損失函數 (Loss)** | 趨近於 0.1 (發生死背現象) | 穩定於 1.0 ~ 2.0 之間 |
| **生成表現** | 發生模板塌陷，反覆噴出標籤 | 語意銜接自然，成功對齊隱含意圖 |

### 訓練公式參考
$$Total Steps = \frac{N_{examples} \times Epochs}{BatchSize \times GradAccum}$$

## 📂 專案結構 (Directory Structure)

```text
.
├── scrapers/              # 資料爬蟲：PTT, Dcard, Threads
├── preprocessing/         # 資料工程：Regex 清洗、標籤標準化、JSONL 合併
├── src/                   # 核心代碼：train.py (Unsloth), test_inference.py
├── demo/                  # 展示介面：chat_demo.py (Gradio UI)
├── requirements.txt       # 環境依賴
└── README.md              # 專案說明文件
```

## 🧪 實驗觀察與 Case Study
模型在 V2 版本中展現了顯著的「風格遷移」能力：

1. 技術諮詢：輸入關鍵字 Transformer 時，模型會切換至結構化輸出的助教模式。

2. 情感共鳴：輸入情緒化語句如 我好像失戀了 時，模型會自動切換至導師人格提供心理支持。

3. 元數據過濾：透過推論端的正則過濾，成功消除了 V1 中常見的日期標籤與論壇特徵雜訊。

## 📦 快速開始
1. 安裝環境:

```Bash

pip install unsloth gradio torch re
```
2. 執行互動介面:

```Bash

python ./chat_demo.py
```
## 🚀 快速推論 (遠端權重版)
本專案已將微調後的 Adapter 託管於 Hugging Face。執行 `chat_demo.py` 時，系統將自動從雲端抓取權重：

```python
# 在代碼中直接修改載入路徑
model = FastLanguageModel.from_pretrained("Li-Kai-Huang/Llama-3-8B-Multi-Persona-Ray")
```
## 🤝 致謝
感謝 Meta 提供 Llama-3 基礎模型，以及 Unsloth 團隊提供的微調加速框架。