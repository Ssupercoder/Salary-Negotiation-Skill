# 9. core/salary_estimator.py
salary_estimator_code = '''"""
薪资预估模块
规则引擎 + OfferShow历史数据
"""
from typing import Dict, Any, Optional, List
from models.schema import SalaryEstimate


class SalaryEstimator:
    """薪资预估器"""

    def __init__(self, data_path: str = "data/salary_data.json"):
        self.data_path = data_path
        self.salary_data = self._load_salary_data()

        self.base_salary_table = {
            ("拼多多", "视觉设计师", "T3-1"): {"base": (50, 75), "total": (80, 120)},
            ("拼多多", "视觉设计师", "T3-2"): {"base": (70, 95), "total": (110, 150)},
            ("拼多多", "算法工程师", "T3-1"): {"base": (55, 80), "total": (90, 130)},
            ("拼多多", "开发工程师", "T3-1"): {"base": (50, 70), "total": (80, 110)},
            ("字节跳动", "视觉设计师", "2-1"): {"base": (35, 50), "total": (60, 85)},
            ("字节跳动", "视觉设计师", "2-2"): {"base": (50, 70), "total": (85, 120)},
            ("字节跳动", "算法工程师", "2-2"): {"base": (55, 75), "total": (90, 125)},
            ("腾讯", "视觉设计师", "T9"): {"base": (40, 55), "total": (65, 90)},
            ("腾讯", "视觉设计师", "T10"): {"base": (55, 75), "total": (90, 120)},
            ("阿里巴巴", "视觉设计师", "P6"): {"base": (45, 65), "total": (75, 100)},
            ("阿里巴巴", "视觉设计师", "P7"): {"base": (65, 90), "total": (100, 140)},
            ("Google", "视觉设计师", "L4"): {"base": (70, 85), "total": (100, 140)},
            ("Google", "视觉设计师", "L5"): {"base": (85, 110), "total": (130, 180)},
        }

        self.education_multiplier = {
            "博士": 1.15, "硕士": 1.08, "本科": 1.0,
            "双非本科": 0.95, "大专": 0.85, "高中": 0.75
        }

    def _load_salary_data(self) -> Dict[str, Any]:
        return {"offershow_2025": {}, "offershow_2026": {}}

    def estimate(self, company: str, role: str, years: float = 0, education: str = "本科",
                 level: Optional[str] = None, has_other_offer: bool = False, skills: Optional[List[str]] = None) -> SalaryEstimate:
        key = (company, role, level)
        if level and key in self.base_salary_table:
            base_range = self.base_salary_table[key]["base"]
            total_range = self.base_salary_table[key]["total"]
        else:
            base_range, total_range = self._fuzzy_match(company, role)

        edu_mult = self.education_multiplier.get(education, 1.0)
        years_mult = min(1 + (years * 0.05), 1.75)

        adjusted_base_min = base_range[0] * edu_mult * years_mult
        adjusted_base_max = base_range[1] * edu_mult * years_mult
        adjusted_total_min = total_range[0] * edu_mult * years_mult
        adjusted_total_max = total_range[1] * edu_mult * years_mult

        if has_other_offer:
            adjusted_base_max *= 1.05
            adjusted_total_max *= 1.05

        if skills:
            scarcity_bonus = self._calculate_scarcity_bonus(skills)
            adjusted_base_max *= (1 + scarcity_bonus)
            adjusted_total_max *= (1 + scarcity_bonus)

        estimated_base = (adjusted_base_min + adjusted_base_max) / 2
        estimated_total = (adjusted_total_min + adjusted_total_max) / 2

        confidence = 0.9 if (level and key in self.base_salary_table) else 0.7
        if not education or years == 0:
            confidence *= 0.8

        return SalaryEstimate(
            company=company, role=role, level=level,
            estimated_base=round(estimated_base, 1),
            estimated_total=round(estimated_total, 1),
            confidence=round(confidence, 2),
            reference_range=(round(adjusted_base_min, 1), round(adjusted_base_max, 1)),
            data_sources=["OfferShow历史数据", "行业薪酬报告"],
            notes=f"基于{company} {role} {'级别' + level if level else '市场'}数据，已应用学历系数{edu_mult:.2f}和年限系数{years_mult:.2f}"
        )

    def _fuzzy_match(self, company: str, role: str) -> tuple:
        company_matches = [v for k, v in self.base_salary_table.items() if k[0] == company]
        if company_matches:
            avg_base_min = sum(m["base"][0] for m in company_matches) / len(company_matches)
            avg_base_max = sum(m["base"][1] for m in company_matches) / len(company_matches)
            avg_total_min = sum(m["total"][0] for m in company_matches) / len(company_matches)
            avg_total_max = sum(m["total"][1] for m in company_matches) / len(company_matches)
            return (avg_base_min, avg_base_max), (avg_total_min, avg_total_max)
        return (35, 50), (55, 80)

    def _calculate_scarcity_bonus(self, skills: List[str]) -> float:
        scarcity_skills = {"AIGC": 0.10, "3D设计": 0.08, "品牌设计": 0.05, "NLP": 0.10,
                           "CV": 0.08, "推荐系统": 0.10, "分布式系统": 0.08, "Go": 0.05, "Rust": 0.08}
        bonus = sum(scarcity_skills.get(skill, 0.0) for skill in skills)
        return min(bonus, 0.20)

    def estimate_from_record(self, record) -> SalaryEstimate:
        return self.estimate(
            company=record.metadata.target_company, role=record.metadata.role,
            years=record.metadata.years, education=record.metadata.education,
            level=record.metadata.target_level, has_other_offer=record.metadata.has_other_offer,
            skills=record.metadata.skills
        )

    def get_market_comparison(self, company: str, role: str, offer_base: float) -> Dict[str, Any]:
        estimate = self.estimate(company, role)
        market_position = "unknown"
        if offer_base < estimate.reference_range[0] * 0.9:
            market_position = "below_market"
        elif offer_base < estimate.reference_range[0]:
            market_position = "low_end"
        elif offer_base <= estimate.reference_range[1]:
            market_position = "market_rate"
        else:
            market_position = "above_market"

        return {
            "offer_base": offer_base,
            "estimated_range": estimate.reference_range,
            "market_position": market_position,
            "position_description": {
                "below_market": "显著低于市场水平，建议争取",
                "low_end": "市场偏低，有谈判空间",
                "market_rate": "符合市场水平",
                "above_market": "高于市场水平，建议接受"
            }.get(market_position, "未知"),
            "estimate": estimate
        }
'''

with open('/mnt/agents/output/salary_negotiation_agent/core/salary_estimator.py', 'w', encoding='utf-8') as f:
    f.write(salary_estimator_code)

print(" core/salary_estimator.py")