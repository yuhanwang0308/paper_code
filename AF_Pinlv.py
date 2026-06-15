import geopandas as gpd
from pathlib import Path

# ===================== 路径（使用上面生成的【完整网格】）=====================
grid_path = r"E:\Data\02_preprocess\sw5\sw5_010gird.shp"
fire_dir = r"E:\Data\01_raw_data\MCD14ML\ActiveFire_shp\sw5"
out_path = r"E:\Data\02_preprocess\sw5\AF_Pi_SW5_010.shp"

# ===================== 读取网格 =====================
grid = gpd.read_file(grid_path)
id_field = "ID"

# ===================== 初始化所有格子 = 0（关键！不会缺格！）=====================
fire_year_count = {fid: 0 for fid in grid[id_field]}

# ===================== 2001-2024 24年 =====================
for year in range(2001, 2025):
    fire_shp = Path(fire_dir) / f"ActiveFire_sw5_{year}.shp"
    if not fire_shp.exists():
        print(f"跳过 {year}")
        continue

    print(f"处理 {year} 年...")
    fire = gpd.read_file(fire_shp)

    # 空间匹配
    join = gpd.sjoin(fire, grid[[id_field, "geometry"]], predicate="within")

    # 有火的格子 +1
    for fid in join[id_field].unique():
        fire_year_count[fid] += 1

# ===================== 计算概率 =====================
grid["fire_years"] = grid[id_field].map(fire_year_count)
grid["fire_prob"] = grid["fire_years"] / 24

# ===================== 导出 =====================
grid.to_file(out_path, encoding="utf-8")

print("\n🎉 最终完成！无缺失、无空白格！")