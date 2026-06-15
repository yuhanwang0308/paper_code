import geopandas as gpd
import numpy as np
from scipy.stats import norm
from pathlib import Path

# ===================== 你的路径（已全部填好）=====================
in_shp = r"E:\Data\01_raw_data\MCD14ML\China\China_AF_count_province.shp"
out_shp = r"E:\Data\01_raw_data\MCD14ML\China\China_AF_province_trend.shp"

# ===================== 1. 读取省级火点统计文件 =====================
gdf = gpd.read_file(in_shp)

# 年份：2003 - 2024
years = list(range(2003, 2025))
year_fields = [f"cnt_{y}" for y in years]
n_years = len(years)

# ===================== 2. 计算 总数 & 年均 =====================
print("正在计算 总数、年均...")

# 火点总数（2003-2024）
gdf["total_0324"] = gdf[year_fields].sum(axis=1).astype(int)

# 年均值
gdf["avg_0324"] = gdf[year_fields].mean(axis=1).round(2)

# ===================== 3. MK 趋势检验 + Sen 斜率 =====================
def mk_sen(ts):
    n = len(ts)
    s = 0
    for i in range(n):
        for j in range(i+1, n):
            s += np.sign(ts[j] - ts[i])

    var_s = n * (n-1) * (2*n +5) / 18

    if s > 0:
        z = (s -1) / np.sqrt(var_s)
    elif s <0:
        z = (s +1) / np.sqrt(var_s)
    else:
        z =0

    p = 2 * (1 - norm.cdf(abs(z)))

    slopes = []
    for i in range(n):
        for j in range(i+1, n):
            slopes.append( (ts[j]-ts[i])/(j-i) )
    sen = np.median(slopes)
    return s, z, p, sen

# 逐省计算
mk_S = []
mk_Z = []
mk_P = []
sen_slope = []
trend_class = []

print("正在逐省计算 MK 趋势检验...")

for idx, row in gdf.iterrows():
    ts = row[year_fields].values.astype(float)
    S, Z, P, Slope = mk_sen(ts)

    mk_S.append(S)
    mk_Z.append(round(Z,3))
    mk_P.append(round(P,3))
    sen_slope.append(round(Slope,3))

    # 趋势分类
    if P < 0.05:
        if Slope >0:
            trend_class.append("显著上升")
        else:
            trend_class.append("显著下降")
    else:
        if Slope>0:
            trend_class.append("不显著上升")
        elif Slope<0:
            trend_class.append("不显著下降")
        else:
            trend_class.append("平稳")

# ===================== 4. 全部写入属性表 =====================
gdf["mk_S"] = mk_S
gdf["mk_Z"] = mk_Z
gdf["mk_p"] = mk_P
gdf["sen_slope"] = sen_slope
gdf["trend"] = trend_class

# ===================== 5. 导出最终 shp =====================
gdf.to_file(out_shp, encoding="utf-8")

print("\n🎉 全部完成！")
print(f"文件已保存到：{out_shp}")
print("\n✅ 新增字段说明：")
print("total_0324   → 2003-2024 火点总数")
print("avg_0324     → 2003-2024 年均火点数量")
print("mk_S         → MK 统计量")
print("mk_Z         → 显著性 Z 值")
print("mk_p         → 显著性 p 值（<0.05 显著）")
print("sen_slope    → 年变化斜率（每年变化量）")
print("trend        → 趋势类型")