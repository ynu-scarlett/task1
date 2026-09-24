# -*- coding: utf-8 -*-
"""
复利 vs 单利 对比程序（在 Step2 / Step3 基础上扩展）

功能：
  1. 交互式输入本金、年利率、存款年限，全部带合法性校验（Step2）
  2. 输出所输入年限的复利本息和
  3. 输出 10 / 20 / 30 年“复利终值 / 单利终值 / 差额”对比表（Step3）
  4. 表格用纯字符串对齐输出，不依赖任何第三方库（中文按两个显示宽度计算）

公式：
  复利终值  A = P × (1 + r) ** t        —— 每年复利 1 次，利息滚入下一年本金
  单利终值  A = P × (1 + r × t)         —— 只有本金生息，利息不再生息
  其中 P 为本金，r 为年利率（小数），t 为存款年数
"""


# ==================== 一、输入与校验 ====================

def read_number(prompt, accept_percent=False):
    """读取一个数字。

    非数字（含空输入、字母）→ 提示“输入无效”并要求重输；
    accept_percent=True 时兼容百分号写法（5% 自动换算为 0.05）。
    """
    while True:
        raw = input(prompt).strip()                 # 读取并去掉首尾空白
        is_percent = accept_percent and raw.endswith("%")  # 是否使用了百分号写法
        raw = raw[:-1] if is_percent else raw       # 百分号写法先去掉末尾的 %
        try:
            value = float(raw)                      # 尝试转浮点数
        except ValueError:
            print("  ⚠ 输入无效，请输入数字！")       # 转换失败 → 重输
            continue
        return value / 100 if is_percent else value  # 5% → 0.05


def read_until_valid(prompt, is_valid, error_msg, accept_percent=False):
    """在 read_number 基础上再做业务规则校验，不满足就打印 error_msg 并重输。"""
    while True:
        value = read_number(prompt, accept_percent=accept_percent)
        if is_valid(value):                         # 满足业务规则（如 > 0、>= 0）
            return value
        print(f"  ⚠ {error_msg}")


# ==================== 二、零依赖对齐字符串表格 ====================

def _char_width(ch):
    """单个字符的显示宽度：中文/全角符号占 2 格，其余占 1 格。"""
    code = ord(ch)
    # CJK 统一汉字、CJK 标点、全角字符、破折号/省略号等按宽字符处理
    if (0x4E00 <= code <= 0x9FFF or          # 汉字
            0x3000 <= code <= 0x303F or      # CJK 标点（、（）等）
            0xFF00 <= code <= 0xFFEF or      # 全角字母符号
            code in (0x2014, 0x2015, 0x2026, 0x2160)):  # —、‖、… 等
        return 2
    return 1


def text_width(text):
    """字符串的终端显示宽度。"""
    return sum(_char_width(ch) for ch in text)


def _pad(text, width, align):
    """按显示宽度补空格对齐：align 可取 left / center / right。"""
    gap = width - text_width(text)
    if gap <= 0:
        return text
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap                      # 默认左对齐


def print_table(headers, rows, aligns):
    """打印竖线分隔的对齐表格（纯字符串，无外部库）。

    headers : 表头字符串列表
    rows    : 每一行的字符串列表（数字请提前格式化好）
    aligns  : 每列对齐方式（left/center/right）
    """
    col_count = len(headers)
    # 每列宽度 = 该列表头与所有单元格显示宽度的最大值
    widths = [
        max([text_width(headers[c])] + [text_width(row[c]) for row in rows])
        for c in range(col_count)
    ]
    line_width = sum(widths) + 3 * (col_count - 1)   # 分隔符 " | " 占 3 格
    border = "-" * line_width

    def build_line(cells):
        return " | ".join(
            _pad(cells[c], widths[c], aligns[c]) for c in range(col_count)
        )

    print(border)
    print(build_line(headers))
    print(border)
    for row in rows:
        print(build_line(row))
    print(border)


# ==================== 三、主流程 ====================

def main():
    print("=" * 50)
    print("           复利 vs 单利 对比计算器")
    print("=" * 50)

    # 1) 本金 P：必须 > 0（≤0 一律拦截）
    P = read_until_valid(
        "请输入本金（元）：",
        is_valid=lambda v: v > 0,
        error_msg="本金必须大于 0，请重新输入！"
    )

    # 2) 年利率 r：必须 ≥ 0（负数拦截并提示“利率不能为负”）；0.05 或 5% 均可
    r = read_until_valid(
        "请输入年利率（小数 0.05 表示 5%，也可直接输入 5%）：",
        is_valid=lambda v: v >= 0,
        error_msg="利率不能为负，请重新输入！",
        accept_percent=True
    )

    # 3) 存款年限 t：必须 > 0（≤0 一律拦截）
    t = read_until_valid(
        "请输入存款年限（年）：",
        is_valid=lambda v: v > 0,
        error_msg="年限必须大于 0，请重新输入！"
    )

    # 4) 所输入年限的复利结果（n = 1，每年复利一次）
    amount = P * (1 + r) ** t                  # 复利终值：(1+r) 的 t 次方
    print()
    print(f"按年复利，存满 {t:g} 年后：本息和 {amount:,.2f} 元"
          f"（其中利息 {amount - P:,.2f} 元）")

    # 5) 10/20/30 年 复利 vs 单利 对比表
    years = (10, 20, 30)
    headers = ["年限", "复利终值(元)", "单利终值(元)", "差额(元)"]
    rows = []
    for year in years:
        compound = P * (1 + r) ** year         # 复利：利滚利
        simple = P * (1 + r * year)            # 单利：仅本金生息
        diff = compound - simple               # 差额 = 复利终值 - 单利终值
        rows.append([
            f"第{year}年",
            f"{compound:,.2f}",
            f"{simple:,.2f}",
            f"{diff:,.2f}",
        ])

    print()
    print(f"本金 {P:,.2f} 元 ｜ 年利率 {r * 100:g}% ｜ 每年复利 1 次")
    print_table(headers, rows, aligns=["center", "right", "right", "right"])
    print("说明：差额 = 复利终值 - 单利终值；年限越久，复利优势越大。")


if __name__ == "__main__":
    main()
