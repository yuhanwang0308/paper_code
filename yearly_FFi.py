import geopandas as gpd
from pathlib import Path

# ===================== 你的路径（已全部填好）=====================
grid_path   = r"E:\Data\02_preprocess\sw5\sw5_005gird.shp"
fire_dir    = r"E:\Data\01_raw_data\MCD14ML\ActiveFire_shp\sw5"
out_path    = r"E:\Data\02_preprocess\sw5\sw5_005_yearly_FFi.shp"

# ===================== 读取网格 =====================
grid = gpd.read_file(grid_path)
id_field = "ID"  # 你的网格ID

# ===================== 逐年统计 2003 - 2024 =====================
for year in range(2003, 2025):
    fire_shp = Path(fire_dir) / f"ActiveFire_sw5_{year}.shp"
    
    if not fire_shp.exists():
        print(f"⚠️ {year} 年文件不存在，赋值 0")
        grid[f"cnt_{year}"] = 0
        continue

    print(f"正在处理：{year} 年")
    fire = gpd.read_file(fire_shp)

    # 空间匹配
    joined = gpd.sjoin(fire, grid[[id_field, "geometry"]], predicate="within")
    
    # 统计当年每个网格的火点数量
    year_count = joined[id_field].value_counts()

    # 赋值到网格：当年字段
    grid[f"cnt_{year}"] = grid[id_field].map(year_count).fillna(0).astype(int)

# ===================== 导出最终网格 =====================
grid.to_file(out_path, encoding="utf-8")

print("\n🎉 全部完成！")
print(f"输出文件：{out_path}")
print("网格属性表中已生成：")
print("cnt_2003, cnt_2004, ..., cnt_2024")
print("每个字段 = 对应年份每个网格的火点数量")