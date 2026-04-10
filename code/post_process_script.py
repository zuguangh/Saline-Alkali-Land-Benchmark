import re
import html
from bs4 import BeautifulSoup


def remove_references_section(text):
    """
    移除参考文献列表内容以及标题
    """
    # 中英文参考文献标题模式
    ref_patterns = [
        r"#+.*参考文献",
        r"#+.*References",
        r"#+.*REFERENCES",
        # 以参考文献开头的行
        r'^.*参考文献',
        r"^.*References",
    ]

    for pattern in ref_patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            # 找到参考文献标题的位置
            ref_start = match.end()
            # 查找下一个章节标题或文档结尾
            next_section = re.search(r"#+\s+[^\n]+\n", text[ref_start:])
            if next_section:
                ref_end = ref_start + next_section.start()
            else:
                ref_end = len(text)

            # 移除参考文献标题及内容
            text = text[:match.start()] + text[ref_end:]
            break

    return text


def remove_image_markup(text):
    """
    移除Markdown格式的图片标记
    """
    # 移除Markdown图片标记
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    return text


def remove_empty_spans(text):
    """
    移除HTML中的空span标签
    """
    soup = BeautifulSoup(text, "html.parser")
    empty_spans = soup.find_all("span", string=lambda x: x is None or x.strip() == "")
    for span in empty_spans:
        span.decompose()

    return str(soup)


def remove_figure_captions(text):
    """
    移除图片指示文字和注释
    """
    # 移除以"图X"或"Figure X"开头的行
    text = re.sub(r"^(图\s*\d+[.:：]?.*?)$", "", text, flags=re.MULTILINE)
    text = re.sub(
        r"^(Fig\s*\d+[.:]?.*?)$", "", text, flags=re.MULTILINE | re.IGNORECASE
    )

    # 移除图片说明注释
    text = re.sub(r"注：.*图中.*$", "", text, flags=re.MULTILINE)
    # 移除图片说明标题
    text = re.sub(r"# 图.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"# Fig.*$", "", text, flags=re.MULTILINE)
    return text


def html_table_to_markdown(html_content):
    """
    将包含合并单元格的HTML表格转换为扁平化的Markdown表格
    """
    # 解析HTML
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")

    if not table:
        return "未找到表格"

    # 获取所有行
    rows = table.find_all("tr")

    # 确定表格的最大列数
    max_cols = 0
    for row in rows:
        col_count = 0
        for cell in row.find_all(["td", "th"]):
            colspan = int(cell.get("colspan", 1))
            col_count += colspan
        max_cols = max(max_cols, col_count)

    # 创建二维数组表示表格
    grid = []
    rowspans = {}  # 存储每列的rowspan信息 {col_index: (value, remaining_rows)}

    for row_idx, row in enumerate(rows):
        grid_row = [""] * max_cols
        col_idx = 0

        # 处理rowspan延续
        for c in range(max_cols):
            if c in rowspans and rowspans[c][1] > 0:
                grid_row[c] = rowspans[c][0]
                rowspans[c] = (rowspans[c][0], rowspans[c][1] - 1)
                if rowspans[c][1] == 0:
                    del rowspans[c]

        # 处理当前行的单元格
        cells = row.find_all(["td", "th"])
        for cell in cells:
            # 跳过已经被rowspan填充的列
            while col_idx < max_cols and grid_row[col_idx]:
                col_idx += 1

            if col_idx >= max_cols:
                break

            # 获取单元格内容
            cell_text = cell.get_text(strip=True)

            # 处理colspan
            colspan = int(cell.get("colspan", 1))
            for i in range(colspan):
                if col_idx + i < max_cols:
                    grid_row[col_idx + i] = cell_text

            # 处理rowspan
            rowspan = int(cell.get("rowspan", 1))
            if rowspan > 1:
                for i in range(colspan):
                    if col_idx + i < max_cols:
                        rowspans[col_idx + i] = (cell_text, rowspan - 1)

            col_idx += colspan

        grid.append(grid_row)

    # 转换为Markdown格式
    if not grid:
        return ""

    # 创建表头分隔线
    header_separator = ["---"] * len(grid[0])

    # 构建Markdown表格
    markdown_lines = []

    # 添加表头
    markdown_lines.append("| " + " | ".join(grid[0]) + " |")
    markdown_lines.append("| " + " | ".join(header_separator) + " |")

    # 添加数据行
    for row in grid[1:]:
        markdown_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(markdown_lines) + "\n"


def extract_and_convert_tables(md_content):
    """
    从Markdown内容中提取HTML表格并转换为Markdown格式
    """
    # 使用正则表达式查找HTML表格
    html_tables = re.findall(r"<table.*?</table>", md_content, re.DOTALL)

    # 转换每个表格
    for html_table in html_tables:
        markdown_table = html_table_to_markdown(html_table)
        if markdown_table:
            md_content = md_content.replace(html_table, markdown_table)

    return md_content


def remove_extra_blank_lines(text):
    """
    移除多余的空行，保留段落间的单个空行
    """
    # 将连续多个空行替换为单个空行
    text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)
    # 移除开头的空行
    text = re.sub(r"^\s*\n", "", text)
    # 移除结尾的空行
    text = re.sub(r"\n\s*$", "", text)

    # 特别处理数学公式周围的空行
    # 查找数学公式前后的空行并移除
    text = re.sub(r"\n\s*\n(\s*\$.+?\$\s*)\n\s*\n", r"\n\1\n", text)
    text = re.sub(r"(\s*\$.+?\$\s*)\n\s*\n", r"\1\n", text)
    text = re.sub(r"\n\s*\n(\s*\$.+?\$\s*)", r"\n\1", text)

    return text


def clean_text(text):
    """
    执行所有清理步骤
    """
    # 按顺序应用所有清理函数
    text = remove_image_markup(text)
    text = remove_empty_spans(text)
    text = remove_figure_captions(text)
    text = extract_and_convert_tables(text)
    text = remove_references_section(text)
    text = remove_extra_blank_lines(text)

    return text


# 使用示例
if __name__ == "__main__":
    # 读取文件内容
    with open(
        "/home/hezg/saline-alkali-soil_llm/盐碱地论文-12篇/不同改良措施对卤阳湖盐碱地土壤性质及玉米产量的影响_徐国凤/不同改良措施对卤阳湖盐碱地土壤性质及玉米产量的影响_徐国凤.md",
        "r",
        encoding="utf-8",
    ) as file:
        content = file.read()

    # 清理文本
    cleaned_content = clean_text(content)

    # 保存清理后的文本
    with open("cleaned_document.md", "w", encoding="utf-8") as file:
        file.write(cleaned_content)

    print("文本清理完成!")
