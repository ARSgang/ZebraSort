import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import os

def infer_plate_size(well_ids):
    rows = sorted(set(w[0] for w in well_ids if isinstance(w, str)))
    cols = sorted(set(int(w[1:]) for w in well_ids if isinstance(w, str)))
    return len(rows), max(cols)

def create_heatmap(data, value_col, n_rows, n_cols, title_suffix, save_folder):
    heatmap = np.full((n_rows, n_cols), np.nan)
    for _, row in data.iterrows():
        match = re.match(r'([A-H])(\d{2})', row["well"])
        if match:
            r = ord(match.group(1)) - ord('A')
            c = int(match.group(2)) - 1
            if r < n_rows and c < n_cols:
                heatmap[r, c] = row[value_col]

    plt.figure(figsize=(n_cols, n_rows))
    sns.heatmap(
        heatmap, annot=True, fmt=".1f",
        cmap="viridis", cbar_kws={"label": value_col}
    )
    plt.title(f"{value_col} Heatmap ({title_suffix})")
    plt.xlabel("Column")
    plt.ylabel("Row")
    plt.xticks(
        ticks=np.arange(n_cols) + 0.5,
        labels=[str(i + 1).zfill(2) for i in range(n_cols)],
        rotation=0
    )
    plt.yticks(
        ticks=np.arange(n_rows) + 0.5,
        labels=[chr(i) for i in range(ord('A'), ord('A') + n_rows)],
        rotation=0
    )
    plt.tight_layout()
    filename = f"heatmap_{value_col}_{title_suffix.replace(' ', '_')}.tif"
    filepath = os.path.join(save_folder, filename)
    plt.savefig(filepath, dpi=300, format='tiff')
    print(f"🖼️ Saved: {filepath}")
    plt.close()

def generate_range(start, end):
    rows = "ABCDEFGH"
    match_start = re.match(r"([A-H])(\d+)", start)
    match_end = re.match(r"([A-H])(\d+)", end)
    if not match_start or not match_end:
        return []
    start_row, start_col = match_start.groups()
    end_row, end_col = match_end.groups()
    start_col = int(start_col)
    end_col = int(end_col)
    result = []

    if start_row == end_row:  # same row
        for col in range(start_col, end_col + 1):
            result.append(f"{start_row}{col:02d}")
    elif start_col == end_col:  # same column
        for r in rows[rows.index(start_row): rows.index(end_row)+1]:
            result.append(f"{r}{start_col:02d}")
    return result

def collect_manual_groups_flex():
    group_dict = {}

    try:
        n_groups = int(input("👥 How many groups do you have? "))
    except ValueError:
        print("❌ Please enter a number.")
        return {}

    group_names = []
    for i in range(n_groups):
        name = input(f"Enter name for group {i+1}: ").strip()
        if name:
            group_names.append(name)

    print("\n👉 Now enter wells for each group using format like:")
    print("   col1(A1-H1) col2(A2-H2) or rowF(F6-F8)\n")

    for group in group_names:
        while True:
            user_input = input(f"🧬 Define wells for group '{group}': ").strip()
            temp_wells = []
            for match in re.findall(r"\(([^()]+)\)", user_input):
                try:
                    start, end = match.strip().split("-")
                    wells = generate_range(start.strip().upper(), end.strip().upper())
                    temp_wells.extend(wells)
                except:
                    print(f"⚠️ Skipped invalid input: {match}")
            print(f"✅ Wells for group '{group}': {', '.join(temp_wells)}")
            confirm = input("✅ Confirm? (Y/n): ").strip().lower()
            if confirm in ["y", "yes", ""]:
                for well in temp_wells:
                    group_dict[well] = group
                break
            else:
                print("🔁 Let's try again for this group.\n")
    return group_dict


def plot_and_export_all(filepath):
    # Step 1: Choose reason
    allowed_reasons = ["TOP_LIGHT", "End of period", "SOUND"]
    print("Choose one of the following end reasons:")
    for i, reason in enumerate(allowed_reasons):
        print(f"{i + 1}. {reason}")
    try:
        choice = int(input("Enter number (1–3): ").strip())
        if choice < 1 or choice > 3:
            raise ValueError
    except ValueError:
        print("❌ Invalid input. Please enter 1, 2, or 3.")
        return
    selected_reason = allowed_reasons[choice - 1]
    print(f"✅ Selected reason: {selected_reason}")

    # Step 2: Load Excel data
    df = pd.read_excel(filepath)
    df_filtered = df[df["endreason"] == selected_reason].copy()
    if df_filtered.empty:
        print("❌ No matching rows found.")
        return

    # Step 3: Extract wells and distances
    df_filtered["well"] = df_filtered["aname"].str.extract(r'([A-H]\d{2})')
    df_filtered = df_filtered.dropna(subset=["well"])
    df_filtered["well"] = df_filtered["well"].str.upper()
    df_filtered["inadist"] = df_filtered["inadist"].fillna(0)
    df_filtered["smldist"] = df_filtered["smldist"].fillna(0)
    df_filtered["lardist"] = df_filtered["lardist"].fillna(0)
    df_filtered["total_distance"] = df_filtered[["inadist", "smldist", "lardist"]].sum(axis=1)

    # Step 4: Ask user to define groups manually
    group_map = collect_manual_groups_flex()
    df_filtered["group"] = df_filtered["well"].map(group_map).fillna("Unknown")

    # Step 5: Export per-well summary (grouped)
    well_summary = df_filtered.groupby(["well", "group"])[["inadist", "smldist", "lardist", "total_distance"]].sum().reset_index()
    well_summary = well_summary.sort_values(by=["group", "well"])
    summary_file = f"distance_summary_{selected_reason.replace(' ', '_')}.xlsx"
    well_summary.to_excel(summary_file, index=False)
    print(f"✅ Per-well summary saved: {summary_file}")


    # Step 6B: Export 4 individual time series files by distance metric
    time_df = df_filtered[["well", "group", "end", "inadist", "smldist", "lardist", "total_distance"]].copy()
    time_df = time_df.rename(columns={"end": "time"})
    
    for metric in ["inadist", "smldist", "lardist", "total_distance"]:
        pivot_df = time_df.pivot(index="time", columns="well", values=metric)

        # Reorder columns based on group and well
        ordered_columns = []
        for group in sorted(time_df["group"].unique()):
            wells_in_group = time_df[time_df["group"] == group]["well"].unique()
            for well in sorted(wells_in_group):
                if well in pivot_df.columns:
                    ordered_columns.append(well)
        pivot_df = pivot_df[ordered_columns]

        # Rename columns to include group (e.g., Control_A01)
        rename_map = {}
        for well in pivot_df.columns:
            group = group_map.get(well, "Unknown")
            rename_map[well] = f"{group}_{well}"
        pivot_df.rename(columns=rename_map, inplace=True)

        filename = f"time_{metric}_{selected_reason.replace(' ', '_')}.xlsx"
        pivot_df.reset_index().to_excel(filename, index=False)
        print(f"📄 Exported: {filename}")


    # Step 7: Plot and save heatmaps
    save_folder = os.getcwd()
    well_ids = well_summary["well"].tolist()
    n_rows, n_cols = infer_plate_size(well_ids)
    for col in ["inadist", "smldist", "lardist", "total_distance"]:
        create_heatmap(well_summary, col, n_rows, n_cols, selected_reason, save_folder)

# 🟢 Run this line (replace filename with yours)
plot_and_export_all("20250618-121409.xlsx")
