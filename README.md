# 美國各州所得稅計算器 - Streamlit 網站

## 背景

根據 Tax Foundation 提供的 2026 年各州所得稅率與級距資料（Excel 檔含 2015-2026 共 12 年資料），建立一個 Streamlit 網站，讓使用者可以：
1. 選擇州別、報稅身分（Single / Married Filing Jointly）
2. 輸入收入金額
3. 計算各級距稅額明細與有效稅率
4. 比較不同州之間的稅負差異

資料涵蓋 50 州 + D.C.，包含：漸進式稅率級距、標準扣除額（Standard Deduction）、個人免稅額（Personal Exemption）等，另有部分州為零稅率（Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Wyoming）以及 Washington（僅對資本利得課稅）。

---

## 專案架構

```
ustax/
├── app.py                          # Streamlit 主程式入口
├── requirements.txt                # 套件依賴
├── data/
│   ├── tax_data_2026.json          # 從 Excel 解析後的結構化 JSON 資料
│   └── footnotes_2026.json         # 註腳說明資料
├── models/
│   ├── __init__.py
│   ├── tax_bracket.py              # TaxBracket 資料類別
│   ├── state_tax_config.py         # StateTaxConfig 資料類別（含扣除額、免稅額）
│   └── filing_status.py            # FilingStatus 列舉
├── services/
│   ├── __init__.py
│   ├── data_loader.py              # DataLoader 負責載入 JSON → 物件
│   ├── tax_calculator.py           # TaxCalculator 核心計算引擎
│   └── comparison_service.py       # ComparisonService 多州比較服務
├── components/
│   ├── __init__.py
│   ├── sidebar.py                  # 側邊欄元件（州別、身分、收入選擇）
│   ├── tax_result.py               # 單州計算結果展示元件
│   ├── comparison_view.py          # 多州比較視圖元件
│   └── charts.py                   # 圖表元件（漸進稅率圖、比較長條圖）
├── utils/
│   ├── __init__.py
│   ├── formatter.py                # 金額/百分比格式化工具
│   └── constants.py                # 常數定義（州名對照等）
└── scripts/
    └── parse_excel.py              # 一次性腳本：Excel → JSON 轉換
```

---

## 資料模型設計

### `FilingStatus` 列舉
```python
class FilingStatus(Enum):
    SINGLE = "single"
    MARRIED_FILING_JOINTLY = "married_filing_jointly"
```

### `TaxBracket` 資料類別
```python
@dataclass
class TaxBracket:
    rate: float          # 稅率，例如 0.02
    min_income: float    # 級距起始金額
    max_income: float    # 級距結束金額（最高級距為 inf）
```

### `StateTaxConfig` 資料類別
```python
@dataclass
class StateTaxConfig:
    state_name: str                     # 全名 e.g. "California"
    state_abbr: str                     # 縮寫 e.g. "Calif."
    has_income_tax: bool                # 是否有所得稅
    is_capital_gains_only: bool         # Washington 特殊情況
    brackets_single: List[TaxBracket]
    brackets_married: List[TaxBracket]
    standard_deduction_single: float    # 0 if n.a.
    standard_deduction_married: float
    personal_exemption_single: float    # 0 if n.a. or credit
    personal_exemption_married: float
    personal_exemption_dependent: float
    exemption_is_credit: bool           # True if "$XXX credit"
    footnotes: List[str]                # 適用的註腳代碼 e.g. ["a","h","j"]
    notes: str                          # 額外說明
```

### `TaxResult` 計算結果
```python
@dataclass
class TaxResult:
    gross_income: float
    standard_deduction: float
    personal_exemption: float
    taxable_income: float
    bracket_details: List[BracketDetail]  # 每一級距的應稅金額與稅額
    total_tax: float
    effective_rate: float                 # total_tax / gross_income
    marginal_rate: float                  # 最高適用稅率
```

---

## 核心計算邏輯 (`TaxCalculator`)

```
Gross Income
  → 減去 Standard Deduction
  → 減去 Personal Exemption（如果不是 credit 形式）
  → 得到 Taxable Income（不低於 0）
  → 對 Taxable Income 套用累進稅率級距，逐級計算
  → 如果 Personal Exemption 是 credit 形式，從稅額中扣除
  → 回傳 TaxResult
```

---

## 頁面功能規劃

### 🏠 頁面一：單州稅額計算
- **側邊欄**：選擇州別（下拉選單含搜尋）、報稅身分、扶養人數、年收入（滑桿 + 數字輸入）
- **主區域**：
  - 稅額摘要卡片（總稅額、有效稅率、邊際稅率）
  - 各級距計算明細表格
  - 累進稅率階梯圖（Plotly 互動圖表）
  - 適用的重要註腳說明

### 📊 頁面二：多州比較
- 選擇 2-10 個州進行比較
- 橫條圖：比較各州稅額
- 折線圖：不同收入水準下的有效稅率比較
- 排名表格：從低到高排序

### 🗺️ 頁面三：全美稅率地圖
- 互動式美國地圖（Plotly choropleth）
- 顏色依有效稅率深淺顯示
- 滑鼠懸停顯示州名、最高稅率、有效稅率
- 可調整收入滑桿，即時更新地圖

---

## Proposed Changes

### 1. 資料處理腳本

#### [NEW] [parse_excel.py](file:///Users/yaolo/Desktop/ustax/scripts/parse_excel.py)
- 讀取 Excel `2026` 工作表
- 解析每個州的稅率級距（Single 與 MFJ 分開）
- 處理特殊情況：
  - 無所得稅州（`'none'`）→ `has_income_tax = False`
  - credit 形式的免稅額（`'$153 credit'`）→ 解析金額並標記
  - Washington 資本利得稅 → `is_capital_gains_only = True`
  - `'n.a.'` → 轉為 0
- 解析註腳代碼（從州名旁的括號中提取）
- 輸出 `data/tax_data_2026.json` 和 `data/footnotes_2026.json`

---

### 2. Models 模組

#### [NEW] [filing_status.py](file:///Users/yaolo/Desktop/ustax/models/filing_status.py)
- `FilingStatus` Enum（SINGLE、MARRIED_FILING_JOINTLY）

#### [NEW] [tax_bracket.py](file:///Users/yaolo/Desktop/ustax/models/tax_bracket.py)
- `TaxBracket` dataclass（rate, min_income, max_income）
- `BracketDetail` dataclass（bracket, taxable_amount, tax_amount — 用於結果展示）

#### [NEW] [state_tax_config.py](file:///Users/yaolo/Desktop/ustax/models/state_tax_config.py)
- `StateTaxConfig` dataclass（完整州稅配置）
- `TaxResult` dataclass（計算結果）

---

### 3. Services 模組

#### [NEW] [data_loader.py](file:///Users/yaolo/Desktop/ustax/services/data_loader.py)
- `DataLoader` 類別
  - `load()` → 從 JSON 載入並建構 `StateTaxConfig` 物件字典
  - `get_state(name)` → 取得單州配置
  - `get_all_states()` → 取得所有州名清單
  - `get_footnote(code)` → 取得註腳文字
- 使用 `@st.cache_data` 快取資料

#### [NEW] [tax_calculator.py](file:///Users/yaolo/Desktop/ustax/services/tax_calculator.py)
- `TaxCalculator` 類別
  - `calculate(gross_income, state_config, filing_status, num_dependents)` → `TaxResult`
  - 內部方法：`_apply_brackets()`, `_get_deduction()`, `_get_exemption()`

#### [NEW] [comparison_service.py](file:///Users/yaolo/Desktop/ustax/services/comparison_service.py)
- `ComparisonService` 類別
  - `compare_states(states, income, filing_status)` → 比較結果 DataFrame
  - `income_curve(states, income_range, filing_status)` → 多州有效稅率曲線資料

---

### 4. Components 模組

#### [NEW] [sidebar.py](file:///Users/yaolo/Desktop/ustax/components/sidebar.py)
- `render_sidebar(data_loader)` → 回傳使用者選擇的參數字典

#### [NEW] [tax_result.py](file:///Users/yaolo/Desktop/ustax/components/tax_result.py)
- `render_tax_result(result, config)` → 顯示摘要指標 + 明細表

#### [NEW] [comparison_view.py](file:///Users/yaolo/Desktop/ustax/components/comparison_view.py)
- `render_comparison(comparison_df, curve_data)` → 顯示比較圖表與排名

#### [NEW] [charts.py](file:///Users/yaolo/Desktop/ustax/components/charts.py)
- `plot_bracket_chart(result)` — 累進稅率階梯圖
- `plot_comparison_bar(comparison_df)` — 多州稅額比較長條圖
- `plot_effective_rate_curve(curve_data)` — 有效稅率曲線
- `plot_us_map(map_data)` — 全美稅率地圖（Plotly choropleth）

---

### 5. Utils 模組

#### [NEW] [formatter.py](file:///Users/yaolo/Desktop/ustax/utils/formatter.py)
- `format_currency(amount)` → `"$1,234.56"`
- `format_percent(rate)` → `"5.25%"`
- `format_income_range(min_val, max_val)` → `"$10,000 – $50,000"`

#### [NEW] [constants.py](file:///Users/yaolo/Desktop/ustax/utils/constants.py)
- `STATE_ABBR_TO_FULL` — 州名縮寫 ↔ 全名對照表（50 州 + D.C.）
- `STATE_FIPS` — 各州 FIPS 代碼（Plotly choropleth 地圖用）
- `NO_INCOME_TAX_STATES` — 無所得稅州清單

---

### 6. 主程式

#### [NEW] [app.py](file:///Users/yaolo/Desktop/ustax/app.py)
- `st.set_page_config()` 設定頁面
- 多頁面導航：稅額計算 / 多州比較 / 全美地圖
- 初始化 `DataLoader`、`TaxCalculator`、`ComparisonService`
- 串接 components 渲染 UI

#### [NEW] [requirements.txt](file:///Users/yaolo/Desktop/ustax/requirements.txt)
```
streamlit>=1.30.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
```

---

## Open Questions（已全數實作）

> [!IMPORTANT]
> **1. 多年度支援？** → ✅ 已實作
> `parse_excel.py` 解析全部 12 個年度工作表（2015-2026），輸出 `data/tax_data_{year}.json` 與 `data/footnotes_{year}.json`。UI 側邊欄可切換課稅年度。年度差異已處理：TN 2015-2020 與 NH 2015-2024 為利息股利稅（工資所得不課稅）、WA 2022 年起課資本利得稅。

> [!IMPORTANT]
> **2. 扶養人數輸入？** → ✅ 已實作
> 三個頁面均支援扶養人數輸入，含扶養免稅額/抵稅額的 credit vs deduction 獨立處理（Arizona、Maine、Utah 等）。

> [!NOTE]
> **3. 特殊規則處理深度？** → ✅ 已實作（2026）
> `services/special_rules.py` 規則引擎 + `data/special_rules.json` 參數檔，2026 年涵蓋：California 免稅額 credit phaseout、Connecticut 免稅額 phaseout 與 recapture、New York recapture、Ohio 分級免稅額、New Mexico 扶養扣除（除一名外）、Vermont 3% AGI 下限與額外標準扣除、Minnesota 標準扣除 phaseout 與投資所得附加稅、Maryland 免稅額 phaseout 與資本利得附加稅、Oregon 免稅額 credit 上限、Maine 可退還扶養 credit、Washington 資本利得稅。其他年度以基本計算＋註腳提醒。新增「資本利得」輸入欄位驅動 WA/MD/MN 規則。已知近似：NY recapture 門檻為 2025 年通膨調整值；MN 附加稅以資本利得近似淨投資所得；Maine 6 歲以下 $610 credit 未建模。

> [!NOTE]
> **4. UI 語言？** → ✅ 已實作
> 雙語介面（繁體中文 / English），側邊欄可切換，預設繁體中文。

---

## Verification Plan

### Automated Tests
- 執行 `parse_excel.py` 確認 JSON 資料正確產生且涵蓋 50 州 + D.C.
- 手動驗算代表性州的計算結果：
  - **California**（10 級距累進稅率）
  - **Florida**（零稅率，稅額應為 0）
  - **Colorado**（單一稅率 4.4%）
  - **New Jersey**（Single 與 MFJ 級距不同）

### Manual Verification
- `streamlit run app.py` 啟動本機伺服器
- 操作每個頁面功能，確認 UI 互動正常
- 對照 Excel 原始資料驗證計算準確性
