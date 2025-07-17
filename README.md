
# 🐟 ZebraSort

A lightweight and flexible tool for rearranging and visualizing **ZebraBox** distance output data.

---

## 🚀 Quick Start

### Option 1: Clone the repository (for Git users)

```bash
git clone https://github.com/ARSgang/ZebraSort.git
cd ZebraSort
```

### Option 2: Manual setup (no Git required)

1. Go to: https://github.com/ARSgang/ZebraSort
2. Click `Code` → `Download ZIP`
3. Extract the folder on your computer
4. Open the folder in your terminal or Anaconda Prompt

---

## 📦 Requirements

Ensure you have **Python ≥ 3.7** and these packages:

```bash
pip install pandas numpy seaborn matplotlib openpyxl
```

---

## ▶️ Run the script

From the ZebraSort folder:

```bash
python zebrasort.py
```

You’ll be prompted to:

- Choose a termination reason (`TOP_LIGHT`, `End of period`, `SOUND`)
- Input how many groups you have
- Define each group's wells using intuitive formats:
  - Columns: `col1(A1-H1)`
  - Rows: `rowF(F6-F8)`
  - Ranges: `(B2-D4)`

---

## 📤 Outputs

ZebraSort saves the following files in the same folder:

| File | Description |
|------|-------------|
| `distance_summary_<REASON>.xlsx` | Total distance per well grouped by condition |
| `time_<metric>_<REASON>.xlsx` | Time-resolved distances for each metric (`inadist`, `smldist`, `lardist`, `total_distance`) |
| `heatmap_<metric>_<REASON>.tif` | Well-plate heatmap of each distance metric |

---

## 🧠 Features

- 🔍 Automatically detects well plate size (6, 12, 24, 48, or 96 wells)
- ✍️ Flexible group input via well range shorthand
- 📊 Clean, analysis-ready Excel output
- 🎨 High-resolution `.tif` heatmaps for visualization

---

## 🐛 Troubleshooting

- Your input Excel must include `aname`, `end`, `endreason`, and at least one distance column (`inadist`, `smldist`, `lardist`)
- Well names should follow format: `A01`, `B03`, `H12` (2-digit columns)
- For Excel compatibility, ensure `openpyxl` is installed

---

## 📜 License

MIT License — free to use, share, and modify with credit.

---

## ✨ Author

Developed by **Trent (ARSgang)** – 2025  
If ZebraSort supports your research, please cite or mention it in your publications.
