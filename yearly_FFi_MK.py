import geopandas as gpd
import numpy as np
from scipy.stats import norm
from pathlib import Path

# ===================== 【你的路径，已填好】 =====================
grid_path = r"E:\Data\02_preprocess\sw5\sw5_005_yearly_FFi.shp"
out_path = r"E:\Data\02_preprocess\sw5\sw5_005_MK_trend.shp"

# ===================== 1. 读取网格 =====================
grid = gpd.read_file(grid_path)
id_field = "ID"

# 年份列表（必须和你属性表里的字段对应）
years = list(range(2003, 2025))  # 2003 - 2024
year_fields = [f"cnt_{y}" for y in years]
n = len(years)

# ===================== 2. 定义 MK 检验 + Sen 斜率函数 =====================
def mann_kendall_sen(ts):
    """
    输入: 时间序列 ts [2003,2004...2024的火点数量]
    输出: S, Z, p_value, sen_slope
    """
    # 1. 计算 MK 统计量 S
    s = 0
    for i in range(n):
        for j in range(i + 1, n):
            s += np.sign(ts[j] - ts[i])

    # 2. 方差 & Z 标准化
    var_s = n * (n - 1) * (2 * n + 5) / 18
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0

    # 3. p 值
    p = 2 * (1 - norm.cdf(abs(z)))

    # 4. Sen 斜率
    slopes = []
    for i in range(n):
        for j in range(i + 1, n):
            slopes.append((ts[j] - ts[i]) / (j - i))
    sen_slope = np.median(slopes)

    return s, z, p, sen_slope

# ===================== 3. 逐网格计算 =====================
mk_S_list = []
mk_Z_list = []
mk_p_list = []
sen_list = []
trend_list = []

for idx, row in grid.iterrows():
    # 取出当前网格 2003-2024 年火点序列
    ts = row[year_fields].values.astype(float)

    # MK + Sen
    S, Z, p, slope = mann_kendall_sen(ts)

    # 趋势分类（论文制图用）
    if p < 0.05:
        if slope > 0:
            trend = "显著上升"
        else:
            trend = "显著下降"
    else:
        if slope > 0:
            trend = "不显著上升"
        elif slope < 0:
            trend = "不显著下降"
        else:
            trend = "稳定"

    mk_S_list.append(S)
    mk_Z_list.append(Z)
    mk_p_list.append(p)
    sen_list.append(slope)
    trend_list.append(trend)

# ===================== 4. 结果写入网格 =====================
grid["mk_S"] = mk_S_list
grid["mk_Z"] = mk_Z_list
grid["mk_p"] = mk_p_list
grid["sen_slope"] = sen_list
grid["trend"] = trend_list

# ===================== 5. 导出 =====================
grid.to_file(out_path, encoding="utf-8")

print("\n🎉 MK 趋势检验完成！")
print(f"输出文件：{out_path}")
print("\n✅ 输出指标说明（论文直接用）：")
print("mk_S      → MK 统计量（正负表示趋势方向）")
print("mk_Z      → 标准化 Z 值（显著性核心）")
print("mk_p      → 显著性 p 值（<0.05 显著）")
print("sen_slope → Sen 斜率（年均变化量）")
print("trend     → 趋势分类（显著上升/显著下降/不显著上升/不显著下降/稳定）")