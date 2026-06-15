import geopandas as gpd
from pathlib import Path

# ===================== 【你的路径，我已经全部填好】 =====================
fire_dir      = r"E:\Data\01_raw_data\MCD14ML\ActiveFire_shp\sw5"  # 火点shp文件夹
grid_path     = r"E:\Data\02_preprocess\sw5\sw5_010gird.shp"       # 0.1度网格
out_grid_path = r"E:\Data\02_preprocess\sw5\sw5_010_FFi.shp"  # 输出结果

# ===================== 1. 读取网格 =====================
grid = gpd.read_file(grid_path)
id_field = "ID"  # 你的网格ID（如果报错改成FID即可）

# 初始化：所有网格频次 = 0
fire_count = {fid: 0 for fid in grid[id_field]}

# ===================== 2. 批量统计 2003-2024 火点总数 =====================
for year in range(2003, 2025):
    fire_shp = Path(fire_dir) / f"ActiveFire_sw5_{year}.shp"
    
    if not fire_shp.exists():
        print(f"跳过 {year}")
        continue

    print(f"正在统计：{year}")
    fire = gpd.read_file(fire_shp)

    # 空间匹配：火点落在哪个网格
    joined = gpd.sjoin(fire, grid[[id_field, "geometry"]], predicate="within")

    # 按网格统计火点数量
    year_count = joined[id_field].value_counts()

    # 累加到总频次
    for fid, cnt in year_count.items():
        fire_count[fid] += cnt

# ===================== 3. 把频次写入网格属性表 =====================
grid["fire_cnt"] = grid[id_field].map(fire_count)

# ===================== 4. 导出 =====================
grid.to_file(out_grid_path, encoding="utf-8")

print("\n✅ 统计完成！")
print(f"输出文件：{out_grid_path}")
print(f"字段 fire_cnt = 2003-2024 每个网格内的火点总频次")