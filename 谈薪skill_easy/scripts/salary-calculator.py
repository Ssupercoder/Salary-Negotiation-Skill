#!/usr/bin/env python3
"""
薪资计算器：根据公司、岗位、级别、年限、学历计算建议薪资范围
"""

def calculate_salary_range(company, role, level, years_exp, education):
    """
    计算建议薪资范围

    Args:
        company: 目标公司（如：拼多多、字节跳动）
        role: 岗位（如：视觉设计师、算法工程师）
        level: 职级（如：T3-1、2-2）
        years_exp: 工作年限
        education: 学历（985/211/海外/普通）

    Returns:
        dict: 包含建议base范围、总包范围、开口价
    """
    # 基础薪资矩阵（视觉设计师示例）
    base_matrix = {
        ('拼多多', 'T3-1'): (50, 75),
        ('拼多多', 'T3-2'): (70, 95),
        ('字节跳动', '2-1'): (35, 50),
        ('字节跳动', '2-2'): (50, 70),
        ('腾讯', 'T9'): (40, 55),
        ('腾讯', 'T10'): (55, 75),
        ('阿里巴巴', 'P6'): (45, 65),
        ('阿里巴巴', 'P7'): (65, 90),
        ('Google中国', 'L4'): (70, 85),
        ('Google中国', 'L5'): (85, 110),
    }

    # 获取基础范围
    key = (company, level)
    if key not in base_matrix:
        return {"error": f"暂无 {company} {level} 的数据，请提供更多信息"}

    base_min, base_max = base_matrix[key]

    # 年限系数（每多1年+2%）
    year_bonus = min(years_exp * 0.02, 0.15)  # 上限15%

    # 学历系数
    edu_bonus = {
        '985': 0.10,
        '211': 0.05,
        '海外': 0.10,
        '普通': 0.0
    }.get(education, 0.0)

    # 计算调整后的范围
    adjusted_min = int(base_min * (1 + year_bonus + edu_bonus))
    adjusted_max = int(base_max * (1 + year_bonus + edu_bonus))

    # 建议开口价（比上限高10-15%）
    opening_offer = int(adjusted_max * 1.12)

    return {
        "company": company,
        "level": level,
        "base_range": f"{adjusted_min}-{adjusted_max}k",
        "opening_offer": f"{opening_offer}k",
        "year_bonus": f"{year_bonus*100:.0f}%",
        "edu_bonus": f"{edu_bonus*100:.0f}%",
        "note": "以上数据为2026年市场参考，实际谈判需结合具体筹码"
    }


if __name__ == "__main__":
    # 示例用法
    result = calculate_salary_range("拼多多", "视觉设计师", "T3-1", 7, "985")
    print(result)
