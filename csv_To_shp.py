import pandas as pd
import geopandas as gpd
from pathlib import Path

# ===================== 路径配置 =====================
csv_dir = r"E:\论文\活跃火数据\原始数据"
out_dir = r"E:\Data\01_raw_data\MCD14ML\ActiveFire_shp\sw5"
boundary_shp = r"E:\Data\01_raw_data\Boundary\China_Prov_City_Conty\SouthWestern\sw5_省.shp"
Path(out_dir).mkdir(parents=True, exist_ok=True)
yn_boundary = gpd.read_file(boundary_shp).union_all()

# ===================== 批量处理 2001-2024 =====================
for year in range(2003, 2025):
    csv_path = Path(csv_dir) / f"modis_{year}_China.csv"
    if not csv_path.exists():
        print(f"跳过 {year}：文件不存在")
        continue

    # 读取CSV
    df = pd.read_csv(csv_path, encoding="gbk", low_memory=False)
    df.columns = df.columns.str.strip().str.lower()

    # 筛选置信度 ≥80
    df = df[df["confidence"] >= 80].copy()

    # 转点 WGS84
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )

    # 裁剪云南省
    gdf_yn = gpd.clip(gdf, yn_boundary)

    # 导出SHP
    out_shp = Path(out_dir) / f"ActiveFire_yn_{year}.shp"
    gdf_yn.to_file(out_shp, encoding="utf-8")
    print(f"✅ {year} 完成 | 火点：{len(gdf_yn)}")
