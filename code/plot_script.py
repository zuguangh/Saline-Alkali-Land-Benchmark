import matplotlib.pyplot as plt
import numpy as np

# 数据准备
# 分组定义 - 按数值排序调整颜色深浅
groups = [
    {
        "name": "Severity",
        "labels": ["mild", "moderate", "severe"],
        "counts": [764, 964, 565],
        "colors": ["#FFEBCD", "#FFE4C4", "#FFF8DC"],
    },
    {
        "name": "Salt Type",
        "labels": ["chloride", "sulphate", "sodic"],
        "counts": [1045, 240, 1494],
        "colors": ["#CCE6FF", "#E6F3FF", "#B3D9FF"],
    },
    {
        "name": "Location",
        "labels": ["coastal", "inland", "secondary"],
        "counts": [1378, 1914, 1104],
        "colors": ["#CCFFCC", "#B3FFB3", "#E6FFE6"],
    },
    {
        "name": "Method",
        "labels": ["engineering", "agronomic", "chemical", "biological"],
        "counts": [1645, 560, 1315, 1006],
        "colors": ["#FF9999", "#FFE6E6", "#FFB3B3", "#FFCCCC"],
    },
]

# 计算柱子位置
bar_width = 0.6
intra_group_gap = 0.2  # 组内间距
inter_group_gap = 1.0  # 组间间距

# 计算每个柱子的位置
positions = []
current_pos = 0
all_labels = []
all_counts = []
all_colors = []

for group in groups:
    for i, label in enumerate(group["labels"]):
        positions.append(current_pos)
        all_labels.append(label)
        all_counts.append(group["counts"][i])
        all_colors.append(group["colors"][i])
        current_pos += bar_width + intra_group_gap
    current_pos += inter_group_gap - intra_group_gap  # 调整组间间距

# 创建图表
fig, ax = plt.subplots(figsize=(8, 8))

# 绘制柱状图
bars = ax.bar(positions, all_counts, color=all_colors, width=bar_width)

# 添加文本标签
ax.set_ylabel("Count", fontsize=18)
ax.set_xlabel("Categories", fontsize=18)

# 添加水平网格线
ax.yaxis.grid(True, linestyle="--", alpha=0.7)
ax.set_axisbelow(True)


# 在柱子上方添加数值标签
def autolabel(bars):
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            "{}".format(height),
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),  # 3点垂直偏移
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=16,
        )


autolabel(bars)

# 设置x轴刻度
ax.set_xticks(positions)
ax.set_xticklabels(all_labels, rotation=45, ha="right", fontsize=16)
# 调整标签位置，使其对齐到柱形中间
for tick in ax.get_xticklabels():
    tick.set_horizontalalignment("right")
    tick.set_x(tick.get_position()[0] + 0.01)

# 调整y轴刻度字号
ax.tick_params(axis="y", labelsize=16)

# 调整布局
plt.tight_layout()

# 保存图表
plt.savefig("dataset_distribution_grouped.pdf", format="pdf", bbox_inches="tight")
print("分组柱状图已成功保存为 'dataset_distribution_grouped.pdf'")
