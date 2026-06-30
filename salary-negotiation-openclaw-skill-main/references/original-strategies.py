# references/original-strategies.py
#
# 这是从 [Ssupercoder/Salary-Negotiation-Skill](https://github.com/Ssupercoder/Salary-Negotiation-Skill)
# 项目 `strategies/negotiation_strategies.py` 摘录的原文,留作本 skill 知识来源的参考。
#
# 原作者:Lei Xin (辛磊, 快手科技) / Zitong Wang (王梓同, 武汉大学) / Hui Wang (王慧)
# 原项目是 Qwen2.5-7B + vLLM 的 Python 服务,本文件仅作为知识蒸馏来源的存档,
# 不作为本仓库的运行依赖。
#
# 本仓库主目录的 SKILL.md 已将这些策略改写为 AI agent 指令文档。
# ---------------------------------------------------------------------------

"""
谈判策略库(原版摘录)
包含反问询价、价值陈述、压力测试、替代补偿等核心策略
"""
from typing import Dict, Any, List
# from models.schema import StrategyTemplate, NegotiationPhase  # 原项目依赖


class StrategyLibrary:
    """谈判策略库(原版)"""

    def __init__(self):
        self.templates = self._init_templates()
        self.scenarios = self._init_scenarios()

    def _init_templates(self) -> Dict[str, Any]:
        return {
            "counter_inquiry": {
                "name": "反问询价",
                "description": "不先报价,让 HR 先暴露预算区间",
                "prompt_template": (
                    "当 HR 问你的期望薪资时,使用反问策略:\n\n"
                    "**推荐话术**:\n"
                    "\"在谈具体数字之前,我想先了解一下这个岗位的薪酬带宽,"
                    "以及贵司对{role}这个级别的定位。基于我目前的背景和手上其他机会,"
                    "我相信我们能找到一个双方都满意的数字。\"\n\n"
                    "**策略解析**:\n"
                    "1. 把球踢回去,让 HR 先暴露预算区间\n"
                    "2. 表明你是有准备的(\"了解级别定位\")\n"
                    "3. 暗示有其他选择(\"手上其他机会\"),但不直接施压"
                ),
            },
            "star_value_statement": {
                "name": "STAR 价值陈述",
                "description": "用 STAR 法则证明自身价值",
                "prompt_template": (
                    "准备 1-2 个核心项目,用 STAR 法则说明你为什么值这个价:\n\n"
                    "**结构**:\n"
                    "- **S (Situation)**:项目背景和挑战\n"
                    "- **T (Task)**:你的任务和职责\n"
                    "- **A (Action)**:你采取的具体行动\n"
                    "- **R (Result)**:量化结果和业务影响"
                ),
            },
            "alternative_compensation": {
                "name": "替代补偿",
                "description": "base 谈不动时争取其他补偿",
                "prompt_template": (
                    "当 HR 说 base 已经到上限时,转向替代补偿:\n\n"
                    "**可谈判的替代补偿项**:\n"
                    "1. **签字费 (Signing Bonus)**:通常 1-6 个月 base\n"
                    "2. **股票/期权**:归属速度、数量、行权价\n"
                    "3. **绩效奖金**:比例、保底、发放频率\n"
                    "4. **职级晋升承诺**:入职后 6 个月评估,提前晋升\n"
                    "5. **其他福利**:搬家费、培训预算、设备补贴"
                ),
            },
            "offer_anchor": {
                "name": "Offer 锚定",
                "description": "利用其他 offer 作为谈判锚点",
                "prompt_template": (
                    "使用其他 offer 作为锚点时的策略:\n\n"
                    "**原则**:\n"
                    "1. **真实性**:只提真实存在的 offer,不要虚构\n"
                    "2. **适度性**:提及但不炫耀,表达倾向性\n"
                    "3. **具体性**:给出具体数字,增强可信度\n\n"
                    "**禁忌**:\n"
                    "- 不要威胁\"不给 XX 我就去别家\"\n"
                    "- 不要透露所有 offer 细节(留有余地)\n"
                    "- 不要过度承诺\"只要给 XX 我一定来\""
                ),
            },
        }

    def _init_scenarios(self) -> Dict[str, Dict[str, Any]]:
        return {
            "budget_limit": {
                "name": "预算有限",
                "hr_line": "这个 offer 已经是这个级别的最高档了,我们确实没有更多预算",
                "risk_level": "medium",
            },
            "anchor_trap": {
                "name": "锚定陷阱",
                "hr_line": "你手上其他 offer 大概什么水平?能透露一下吗?",
                "risk_level": "low",
            },
            "pressure_lowball": {
                "name": "压价试探",
                "hr_line": "你的期望超出我们的预算了,能不能再低点?比如 65k?",
                "risk_level": "high",
            },
            "time_pressure": {
                "name": "时间压力",
                "hr_line": "这个 offer 本周内必须确认,过期就作废了",
                "risk_level": "medium",
            },
            "level_downplay": {
                "name": "职级压低",
                "hr_line": "我们只能给你定 T3-1,虽然你经验很丰富,但我们的职级体系比较严格",
                "risk_level": "high",
            },
        }

    def _suggest_opening_price(self, background: Dict[str, Any]) -> Dict[str, Any]:
        """原项目的开场价算法:期望上限 × 1.12 / × 0.95 / × 1.20"""
        expected_max = background.get("expected_salary_max", 0)
        if expected_max:
            return {
                "suggested": int(expected_max * 1.12),
                "rationale": "比期望上限高 12%,留出谈判空间",
                "floor": int(expected_max * 0.95),
                "ceiling": int(expected_max * 1.20),
            }
        return {"suggested": 0, "rationale": "请提供期望薪资", "floor": 0, "ceiling": 0}


if __name__ == "__main__":
    lib = StrategyLibrary()
    print(f"策略数: {len(lib.templates)}")
    print(f"场景数: {len(lib.scenarios)}")
    print(f"开场价示例(期望 80k): {lib._suggest_opening_price({'expected_salary_max': 80})}")