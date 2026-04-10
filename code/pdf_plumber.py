import pdfplumber


filename = "水旱轮作、灌排协同及施肥联控对盐碱地土壤及作物的影响_张萌"

with pdfplumber.open(filename + ".pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"  # 逐页提取文本
print(text)

# 打开（或创建）文件并写入内容
with open("pdfplumber/" + filename + ".text", "w") as file:
    file.write(text)

with pdfplumber.open(filename + ".pdf") as pdf:
    for page in pdf.pages:
        table = page.extract_table()  # 提取当前页的第一个表格
        if table:
            for row in table:
                print(row)  # 每行数据为列表
        else:
            print("No table found on this page.")
