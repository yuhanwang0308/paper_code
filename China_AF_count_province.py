import geopandas as gpd
from pathlib import Path

# ===================== 【你的所有路径，已填好】 =====================
boundary_path = r"E:\Data\01_raw_data\Boundary\China_Prov_City_Conty\中国_省_市_县\中国_省_Areas.shp"
fire_shp_dir  = r"E:\Data\01_raw_data\MCD14ML\China\AFshp"  # 火点shp路径
out_shp       = r"E:\Data\01_raw_data\MCD14ML\China\China_AF_count_province.shp"



# ===================== 1. 读取省级行政区划 =====================
province = gpd.read_file(boundary_path)
province = province.copy()  # 复制一份，不修改原始数据
id_field = "ID"  # 省级区划唯一ID，无需修改

# ===================== 2. 批量读取每年火点，逐省统计 =====================
fire_files = list(Path(fire_shp_dir).glob("modis_20??_China.shp"))
fire_files.sort()

print(f"✅ 找到 {len(fire_files)} 年火点数据")

for fire_shp in fire_files:
    # 提取年份 20xx
    year = fire_shp.stem.split("_")[1]
    field_name = f"cnt_{year}"
    print(f"\n正在统计：{year} 年各省火点数量")

    # 读取火点
    fire = gpd.read_file(fire_shp)

    # 空间连接：火点落在哪个省
    joined = gpd.sjoin(fire, province[[id_field, "geometry"]], predicate="within")

    # 按省统计火点数量
    count = joined[id_field].value_counts()

    # 写入行政区划属性表
    province[field_name] = province[id_field].map(count).fillna(0).astype(int)

# ===================== 3. 导出最终结果 =====================
province.to_file(out_shp, encoding="utf-8")

print("\n🎉 全部统计完成！")
print(f"输出文件：{out_shp}")
print("\n✅ 省级区划属性表已生成每年火点数字段：")
print("cnt_2003, cnt_2004, ..., cnt_2024")
print("每个字段 = 该省当年火点总数")