
# 3. models/state_machine.py
state_machine_code = '''"""
谈薪五阶段状态机引擎
管理用户从信息收集到最终决策的完整流程
"""
from typing import Dict, List, Optional, Any
from enum import Enum
from models.schema import NegotiationPhase, UserMetadata


class PhaseRequirement(str, Enum):
    """阶段必要信息要求"""
    TARGET_COMPANY = "target_company"
    ROLE = "role"
    YEARS = "years"
    EDUCATION = "education"
    EXPECTED_SALARY = "expected_salary"
    HAS_OTHER_OFFER = "has_other_offer"
    CURRENT_SALARY = "current_salary"
    TARGET_LEVEL = "target_level"
    DEADLINE = "deadline"


class PhaseConfig:
    """阶段配置"""
    def __init__(
        self,
        phase: NegotiationPhase,
        required_info: List[PhaseRequirement],
        optional_info: List[PhaseRequirement],
        next_phases: List[NegotiationPhase],
        entry_conditions: List[str],
        exit_conditions: List[str]
    ):
        self.phase = phase
        self.required_info = required_info
        self.optional_info = optional_info
        self.next_phases = next_phases
        self.entry_conditions = entry_conditions
        self.exit_conditions = exit_conditions


class NegotiationStateMachine:
    """谈薪状态机"""

    PHASE_CONFIGS = {
        NegotiationPhase.P1_INFO_GATHERING: PhaseConfig(
            phase=NegotiationPhase.P1_INFO_GATHERING,
            required_info=[
                PhaseRequirement.TARGET_COMPANY,
                PhaseRequirement.ROLE,
                PhaseRequirement.YEARS,
                PhaseRequirement.EDUCATION,
            ],
            optional_info=[
                PhaseRequirement.EXPECTED_SALARY,
                PhaseRequirement.HAS_OTHER_OFFER,
                PhaseRequirement.CURRENT_SALARY,
                PhaseRequirement.TARGET_LEVEL,
                PhaseRequirement.DEADLINE,
            ],
            next_phases=[NegotiationPhase.P2_STRATEGY_FORMULATION],
            entry_conditions=["用户开始谈薪咨询"],
            exit_conditions=["已收集必要信息，用户要求制定策略"]
        ),
        NegotiationPhase.P2_STRATEGY_FORMULATION: PhaseConfig(
            phase=NegotiationPhase.P2_STRATEGY_FORMULATION,
            required_info=[
                PhaseRequirement.EXPECTED_SALARY,
                PhaseRequirement.HAS_OTHER_OFFER,
            ],
            optional_info=[
                PhaseRequirement.CURRENT_SALARY,
                PhaseRequirement.TARGET_LEVEL,
            ],
            next_phases=[
                NegotiationPhase.P3_PRACTICE_NEGOTIATION,
                NegotiationPhase.P4_DECISION_SUPPORT
            ],
            entry_conditions=["信息收集完成"],
            exit_conditions=["策略已制定，用户准备谈判或已拿到offer"]
        ),
        NegotiationPhase.P3_PRACTICE_NEGOTIATION: PhaseConfig(
            phase=NegotiationPhase.P3_PRACTICE_NEGOTIATION,
            required_info=[],
            optional_info=[],
            next_phases=[
                NegotiationPhase.P2_STRATEGY_FORMULATION,
                NegotiationPhase.P4_DECISION_SUPPORT
            ],
            entry_conditions=["用户请求模拟谈判"],
            exit_conditions=["用户完成模拟或拿到真实offer"]
        ),
        NegotiationPhase.P4_DECISION_SUPPORT: PhaseConfig(
            phase=NegotiationPhase.P4_DECISION_SUPPORT,
            required_info=[],
            optional_info=[],
            next_phases=[NegotiationPhase.P5_POST_NEGOTIATION],
            entry_conditions=["用户拿到offer或谈判结果"],
            exit_conditions=["用户做出决策"]
        ),
        NegotiationPhase.P5_POST_NEGOTIATION: PhaseConfig(
            phase=NegotiationPhase.P5_POST_NEGOTIATION,
            required_info=[],
            optional_info=[],
            next_phases=[],
            entry_conditions=["用户接受或拒绝offer"],
            exit_conditions=["流程结束"]
        )
    }

    def __init__(self, user_metadata: UserMetadata):
        self.user_metadata = user_metadata
        self.current_phase = NegotiationPhase.P1_INFO_GATHERING
        self.phase_history: List[NegotiationPhase] = []
        self.extracted_info: Dict[str, Any] = {}
        self.info_completeness: Dict[str, bool] = {}

    def get_current_config(self) -> PhaseConfig:
        """获取当前阶段配置"""
        return self.PHASE_CONFIGS[self.current_phase]

    def check_info_completeness(self) -> Dict[str, Any]:
        """检查当前阶段信息完整度"""
        config = self.get_current_config()
        completeness = {}

        for req in config.required_info:
            value = self._get_info_value(req)
            completeness[req.value] = {
                "required": True,
                "filled": value is not None and value != "",
                "value": value
            }

        for req in config.optional_info:
            value = self._get_info_value(req)
            completeness[req.value] = {
                "required": False,
                "filled": value is not None and value != "",
                "value": value
            }

        return completeness

    def _get_info_value(self, req: PhaseRequirement) -> Any:
        """从metadata获取信息值"""
        mapping = {
            PhaseRequirement.TARGET_COMPANY: self.user_metadata.target_company,
            PhaseRequirement.ROLE: self.user_metadata.role,
            PhaseRequirement.YEARS: self.user_metadata.years,
            PhaseRequirement.EDUCATION: self.user_metadata.education,
            PhaseRequirement.EXPECTED_SALARY: (self.user_metadata.expected_salary_min,
                                                self.user_metadata.expected_salary_max),
            PhaseRequirement.HAS_OTHER_OFFER: self.user_metadata.has_other_offer,
            PhaseRequirement.CURRENT_SALARY: self.user_metadata.current_salary,
            PhaseRequirement.TARGET_LEVEL: self.user_metadata.target_level,
            PhaseRequirement.DEADLINE: self.user_metadata.deadline,
        }
        return mapping.get(req)

    def can_advance(self) -> bool:
        """判断是否可进入下一阶段"""
        completeness = self.check_info_completeness()
        required_items = [v for k, v in completeness.items() if v["required"]]
        return all(item["filled"] for item in required_items)

    def advance_phase(self, target_phase: Optional[NegotiationPhase] = None) -> NegotiationPhase:
        """推进到下一阶段"""
        self.phase_history.append(self.current_phase)

        if target_phase and target_phase in self.get_current_config().next_phases:
            self.current_phase = target_phase
        elif self.can_advance() and self.get_current_config().next_phases:
            self.current_phase = self.get_current_config().next_phases[0]

        return self.current_phase

    def get_missing_info_prompt(self) -> str:
        """生成缺失信息追问提示"""
        completeness = self.check_info_completeness()
        missing = [k for k, v in completeness.items() if v["required"] and not v["filled"]]

        prompts = {
            "target_company": "你面试的是哪家公司？",
            "role": "你应聘的是什么岗位？",
            "years": "你有多少年工作经验？",
            "education": "你的学历背景是什么？",
            "expected_salary": "你的期望薪资区间是多少？",
            "has_other_offer": "你手上还有其他offer吗？",
            "current_salary": "你目前的薪资是多少？",
            "target_level": "对方给你定的职级是什么？",
            "deadline": "HR给的确认deadline是什么时候？",
        }

        questions = [prompts.get(m, f"请补充{m}") for m in missing]
        return "\\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)]) if questions else ""

    def get_phase_guidance(self) -> str:
        """获取当前阶段引导语"""
        guidance = {
            NegotiationPhase.P1_INFO_GATHERING: "我们先来收集你的背景信息，这有助于制定最佳策略。",
            NegotiationPhase.P2_STRATEGY_FORMULATION: "信息收集完成，现在为你制定谈判策略。",
            NegotiationPhase.P3_PRACTICE_NEGOTIATION: "我们来模拟一下谈判场景，帮你熟悉话术。",
            NegotiationPhase.P4_DECISION_SUPPORT: "基于谈判结果，我帮你分析利弊。",
            NegotiationPhase.P5_POST_NEGOTIATION: "恭喜！我们来确认后续事项。"
        }
        return guidance.get(self.current_phase, "")

    def update_extracted_info(self, key: str, value: Any):
        """更新提取的信息"""
        self.extracted_info[key] = value
        if hasattr(self.user_metadata, key):
            setattr(self.user_metadata, key, value)

    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            "current_phase": self.current_phase.value,
            "phase_history": [p.value for p in self.phase_history],
            "completeness": self.check_info_completeness(),
            "can_advance": self.can_advance(),
            "extracted_info": self.extracted_info
        }
'''

with open('/mnt/agents/output/salary_negotiation_agent/models/state_machine.py', 'w', encoding='utf-8') as f:
    f.write(state_machine_code)

print(" models/state_machine.py")

