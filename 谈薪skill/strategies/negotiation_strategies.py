
# 12. strategies/negotiation_strategies.py
strategies_code = '''"""
谈判策略库
包含反问询价、价值陈述、压力测试、替代补偿等核心策略
"""
from typing import Dict, Any, List
from models.schema import StrategyTemplate, NegotiationPhase


class StrategyLibrary:
    """谈判策略库"""

    def __init__(self):
        self.templates = self._init_templates()
        self.scenarios = self._init_scenarios()

    def _init_templates(self) -> Dict[str, StrategyTemplate]:
        return {
            "counter_inquiry": StrategyTemplate(
                name="反问询价",
                description="不先报价，让HR先暴露预算区间",
                applicable_phases=[NegotiationPhase.P2_STRATEGY_FORMULATION, NegotiationPhase.P3_PRACTICE_NEGOTIATION],
                prompt_template="""当HR问你的期望薪资时，使用反问策略：\n\n**推荐话术**：\n"在谈具体数字之前，我想先了解一下这个岗位的薪酬带宽，以及贵司对{role}这个级别的定位。基于我目前的背景和手上其他机会，我相信我们能找到一个双方都满意的数字。"\n\n**策略解析**：\n1. 把球踢回去，让HR先暴露预算区间\n2. 表明你是有准备的（"了解级别定位"）\n3. 暗示有其他选择（"手上其他机会"），但不直接施压\n\n**如果HR坚持要你先说**：\n给出一个范围而非具体数字："我了解市场上这个级别的价位在{min_salary}k-{max_salary}k之间，基于我的经验和技能，我期望在这个区间偏上的位置。"\n""",
                example_responses=["在谈具体数字之前，我想先了解一下这个岗位的薪酬带宽...", "我了解市场上这个级别的价位在65k-90k之间..."]
            ),
            "star_value_statement": StrategyTemplate(
                name="STAR价值陈述",
                description="用STAR法则证明自身价值",
                applicable_phases=[NegotiationPhase.P2_STRATEGY_FORMULATION, NegotiationPhase.P3_PRACTICE_NEGOTIATION],
                prompt_template="""准备1-2个核心项目，用STAR法则说明你为什么值这个价：\n\n**结构**：\n- **S (Situation)**：项目背景和挑战\n- **T (Task)**：你的任务和职责\n- **A (Action)**：你采取的具体行动\n- **R (Result)**：量化结果和业务影响\n\n**示例**：\n"在上一家公司，我负责的品牌升级项目（S），需要在3个月内完成全渠道视觉体系重构（T）。我主导了设计系统搭建，协调了5人小组，引入了AIGC辅助流程（A），最终提前2周交付，用户品牌认知度提升35%，设计效率提升50%（R）。"\n\n**关键要点**：\n1. 结果必须量化（百分比、金额、时间）\n2. 强调与目标岗位的契合度\n3. 突出稀缺技能（如AIGC、3D、品牌全案）\n""",
                example_responses=["在上一家公司，我负责的品牌升级项目...", "我主导的3D设计系统搭建，让设计效率提升50%..."]
            ),
            "alternative_compensation": StrategyTemplate(
                name="替代补偿",
                description="base谈不动时争取其他补偿",
                applicable_phases=[NegotiationPhase.P3_PRACTICE_NEGOTIATION, NegotiationPhase.P4_DECISION_SUPPORT],
                prompt_template="""当HR说base已经到上限时，转向替代补偿：\n\n**可谈判的替代补偿项**：\n1. **签字费 (Signing Bonus)**：通常1-6个月base，谈判空间较大\n2. **股票/期权**：归属速度、数量、行权价\n3. **绩效奖金**：比例、保底、发放频率\n4. **职级晋升承诺**：入职后6个月评估，提前晋升\n5. **其他福利**：搬家费、培训预算、设备补贴\n\n**话术示例**：\n"理解贵司的预算管理。如果base确实到了上限，能否在签字费或股票归属速度上做一些调整？这些对我来说也有实质价值。我目前另一个机会在总包上更有竞争力，但我更倾向贵司的平台，所以希望能找到一个平衡点。"\n\n**注意事项**：\n- 签字费通常是一次性的，不要过度依赖\n- 股票要确认归属条件和离职处理\n- 所有承诺要求书面确认\n""",
                example_responses=["如果base确实到了上限，能否在签字费上做一些调整？", "能否将股票归属期从4年缩短到3年？"]
            ),
            "offer_anchor": StrategyTemplate(
                name="Offer锚定",
                description="利用其他offer作为谈判锚点",
                applicable_phases=[NegotiationPhase.P2_STRATEGY_FORMULATION, NegotiationPhase.P3_PRACTICE_NEGOTIATION],
                prompt_template="""使用其他offer作为锚点时的策略：\n\n**原则**：\n1. **真实性**：只提真实存在的offer，不要虚构\n2. **适度性**：提及但不炫耀，表达倾向性\n3. **具体性**：给出具体数字，增强可信度\n\n**话术示例**：\n"我目前手上有一个Google中国的offer，base 75k，总包约110万。但我更看好贵司的业务方向和成长空间，所以如果总包能接近这个水平，我会优先选择贵司。"\n\n**进阶技巧**：\n- 如果offer来自更知名公司，强调"平台选择"而非"薪资对比"\n- 如果offer薪资更高，强调"长期发展"而非"短期收入"\n- 如果offer来自小公司，强调"稳定性"和"大平台价值"\n\n**禁忌**：\n- 不要威胁"不给XX我就去别家"\n- 不要透露所有offer细节（留有余地）\n- 不要过度承诺"只要给XX我一定来"\n""",
                example_responses=["我目前手上有一个Google的offer，但我更看好贵司...", "另一个机会在总包上更有竞争力，但我更倾向贵司的平台..."]
            )
        }

    def _init_scenarios(self) -> Dict[str, Dict[str, Any]]:
        return {
            "budget_limit": {
                "name": "预算有限",
                "hr_line": "这个offer已经是这个级别的最高档了，我们确实没有更多预算",
                "wrong_response": "那好吧，我接受（直接放弃谈判空间）",
                "correct_response": """"理解贵司的预算管理。想确认一下，这个上限是视觉设计师的统一标准，还是针对我这个specific offer的？另外，如果base确实到了上限，能否在签字费或股票归属速度上做一些调整？这些对我来说也有实质价值。"\n\n**策略解析**：先确认预算有限的真实性（是统一标准还是个体case），然后转向替代补偿。""",
                "risk_level": "medium",
                "follow_up": ["如果HR说统一标准", "如果HR说确实没空间"]
            },
            "anchor_trap": {
                "name": "锚定陷阱",
                "hr_line": "你手上其他offer大概什么水平？能透露一下吗？",
                "wrong_response": "我期望80k（直接暴露底线）",
                "correct_response": """"在谈具体数字之前，我想先了解一下这个岗位的薪酬带宽，以及贵司对视觉设计师这个级别的定位。基于我目前的背景和手上其他机会，我相信我们能找到一个双方都满意的数字。"\n\n**策略解析**：把球踢回去，让HR先暴露预算区间。如果HR坚持要你先说，给一个范围而非具体数字。""",
                "risk_level": "low",
                "follow_up": ["如果HR坚持要你先说数字", "如果HR给出预算区间"]
            },
            "pressure_lowball": {
                "name": "压价试探",
                "hr_line": "你的期望超出我们的预算了，能不能再低点？比如65k？",
                "wrong_response": "那70k可以吗？（直接降价）",
                "correct_response": """"感谢反馈。我想确认一下，65k是基于我这个specific背景（7年经验+AIGC+品牌全案）的评估，还是这个级别的统一标准？另外，我想重申一下我带来的价值：在上一家公司，我主导的品牌升级项目让用户认知度提升35%，设计效率提升50%。基于这些可量化的成果，我相信我的期望是合理的。"\n\n**策略解析**：不要直接降价，先质疑定价依据，然后用STAR法则重申价值。""",
                "risk_level": "high",
                "follow_up": ["如果HR坚持65k", "如果HR松口到70k"]
            },
            "time_pressure": {
                "name": "时间压力",
                "hr_line": "这个offer本周内必须确认，过期就作废了",
                "wrong_response": "那我马上确认（被时间压力迫使仓促决定）",
                "correct_response": """"理解贵司的招聘流程有时间要求。能否确认一下，这个deadline是硬性要求还是有弹性空间？因为我需要充分评估这个机会，包括和家人的商量。如果确实时间紧张，我可以在明天下班前给您明确答复。"\n\n**策略解析**：不要立即答应，争取思考时间。同时暗示你有评估标准（"和家人商量"），不是 desperation mode。""",
                "risk_level": "medium",
                "follow_up": ["如果HR说deadline是硬性", "如果HR同意延期"]
            },
            "level_downplay": {
                "name": "职级压低",
                "hr_line": "我们只能给你定T3-1，虽然你经验很丰富，但我们的职级体系比较严格",
                "wrong_response": "好吧，T3-1就T3-1（接受低职级）",
                "correct_response": """"理解贵司的职级体系。想确认一下，T3-1的定级是基于我目前的背景评估，还是统一标准？因为我在上一家公司已经带3人团队，负责核心模块，且项目量级和成果都达到了更高标准。如果定级确实无法调整，能否在薪资上反映这部分价值差异？"\n\n**策略解析**：质疑定级依据，用具体经历证明应该更高，然后转向薪资补偿。""",
                "risk_level": "high",
                "follow_up": ["如果HR坚持T3-1", "如果HR同意重新评估"]
            }
        }

    def get_strategy(self, strategy_name: str) -> StrategyTemplate:
        return self.templates.get(strategy_name)

    def get_pressure_test_scenario(self, scenario_name: str) -> str:
        scenario = self.scenarios.get(scenario_name)
        if not scenario:
            return "场景不存在"
        return f"""**场景：{scenario['name']}**\n\nHR："{scenario['hr_line']}"\n\n**❌ 错误回法**：\n{scenario['wrong_response']}\n\n**✅ 推荐回法**：\n{scenario['correct_response']}\n\n**⚠️ 风险等级**：{scenario['risk_level']}\n\n**后续跟进**：\n{chr(10).join([f"• {f}" for f in scenario['follow_up']])}\n"""

    def get_all_scenarios(self) -> List[str]:
        return list(self.scenarios.keys())

    def get_applicable_strategies(self, phase: NegotiationPhase) -> List[StrategyTemplate]:
        return [template for template in self.templates.values() if phase in template.applicable_phases]

    def generate_custom_strategy(self, user_background: Dict[str, Any], target_company: str, target_role: str) -> Dict[str, Any]:
        strategies = []
        if user_background.get("has_other_offer"):
            strategies.append({"strategy": "offer_anchor", "priority": "high", "reason": "手上有其他offer，可作为锚定筹码"})
        if user_background.get("years", 0) >= 5:
            strategies.append({"strategy": "star_value_statement", "priority": "high", "reason": "资深经验，需要用STAR法则证明价值"})
        if user_background.get("is_new_grad"):
            strategies.append({"strategy": "alternative_compensation", "priority": "medium", "reason": "应届生base谈判空间有限，可争取签字费和培训"})
        return {
            "target_company": target_company,
            "target_role": target_role,
            "recommended_strategies": strategies,
            "opening_price_suggestion": self._suggest_opening_price(user_background),
            "fallback_plan": "如果base谈不动，争取签字费+股票归属加速"
        }

    def _suggest_opening_price(self, background: Dict[str, Any]) -> Dict[str, Any]:
        expected_max = background.get("expected_salary_max", 0)
        if expected_max:
            return {"suggested": int(expected_max * 1.12), "rationale": "比期望上限高12%，留出谈判空间", "floor": int(expected_max * 0.95), "ceiling": int(expected_max * 1.20)}
        return {"suggested": 0, "rationale": "请提供期望薪资", "floor": 0, "ceiling": 0}
'''

with open('/mnt/agents/output/salary_negotiation_agent/strategies/negotiation_strategies.py', 'w', encoding='utf-8') as f:
    f.write(strategies_code)

print(" strategies/negotiation_strategies.py")

