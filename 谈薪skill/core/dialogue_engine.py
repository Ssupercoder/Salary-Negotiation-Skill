
# 7. core/dialogue_engine.py
dialogue_engine_code = '''"""
核心对话引擎
基于Qwen2.5-7B-Instruct，结合状态机和策略生成回复
"""
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.schema import NegotiationPhase, DialogueResponse, ConversationTurn, UserMetadata, RAGDocument, IntentType
from models.state_machine import NegotiationStateMachine
from core.intent_classifier import IntentClassifier
from core.rag_retriever import RAGRetriever
from core.salary_estimator import SalaryEstimator
from strategies.negotiation_strategies import StrategyLibrary


class DialogueEngine:
    """核心对话引擎"""

    def __init__(self, model_name: str = "Qwen/Qwen2.5-7B-Instruct", use_vllm: bool = True, quantization: str = "INT8"):
        self.model_name = model_name
        self.use_vllm = use_vllm
        self.quantization = quantization
        self.intent_classifier = IntentClassifier()
        self.rag_retriever = RAGRetriever()
        self.salary_estimator = SalaryEstimator()
        self.strategy_library = StrategyLibrary()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def initialize_session(self, session_id: str, user_metadata: UserMetadata) -> Dict[str, Any]:
        state_machine = NegotiationStateMachine(user_metadata)
        session = {
            "session_id": session_id,
            "user_metadata": user_metadata,
            "state_machine": state_machine,
            "conversation_history": [],
            "created_at": datetime.now(),
            "last_active": datetime.now()
        }
        self.sessions[session_id] = session
        return session

    def process_turn(self, session_id: str, user_input: str, input_type: str = "text") -> DialogueResponse:
        session = self.sessions.get(session_id)
        if not session:
            return self._create_error_response("会话未初始化，请先提供背景信息")

        state_machine = session["state_machine"]
        conversation_history = session["conversation_history"]

        user_turn = ConversationTurn(
            from_="human",
            value=user_input,
            metadata={
                "phase": state_machine.current_phase.value,
                "round": len(conversation_history) + 1,
                "speaker": "user",
                "input_type": input_type
            }
        )
        conversation_history.append(user_turn)

        intent_result = self.intent_classifier.classify_with_phase_context(
            user_input, state_machine.current_phase.value, conversation_history
        )

        self._extract_and_update_info(user_input, state_machine)

        if state_machine.can_advance() and intent_result["intent"] in [IntentType.STRATEGY_REQUEST, IntentType.ROLE_PLAY]:
            state_machine.advance_phase()

        response = self._generate_response(
            user_input=user_input,
            intent=intent_result["intent"],
            state_machine=state_machine,
            conversation_history=conversation_history
        )

        agent_turn = ConversationTurn(
            from_="gpt",
            value=response.content,
            metadata={
                "phase": response.phase.value,
                "round": len(conversation_history) + 1,
                "speaker": "agent",
                "strategy": response.strategy,
                "intent": intent_result["intent"].value
            }
        )
        conversation_history.append(agent_turn)
        session["last_active"] = datetime.now()

        return response

    def _extract_and_update_info(self, text: str, state_machine: NegotiationStateMachine):
        salary_patterns = [
            r"(?:目前|当前|现在).*?(?:薪资|工资|base).*?(\\d+[\\.\\d]*).*?[kK万]",
            r"(?:期望|想要|希望).*?(?:薪资|工资|base).*?(\\d+[\\.\\d]*).*?[kK万]",
            r"(?:手上|其他).*?offer.*?(\\d+[\\.\\d]*).*?[kK万]",
            r"base\\s*(\\d+[\\.\\d]*)"
        ]
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary = float(match.group(1))
                if "目前" in text or "当前" in text or "现在" in text:
                    state_machine.update_extracted_info("current_salary", salary)
                elif "期望" in text or "想要" in text or "希望" in text:
                    if "上限" in text or "最高" in text:
                        state_machine.update_extracted_info("expected_salary_max", salary)
                    else:
                        state_machine.update_extracted_info("expected_salary_min", salary)
                elif "offer" in text.lower():
                    state_machine.update_extracted_info("has_other_offer", True)

        company_pattern = r"(字节跳动|腾讯|阿里巴巴|拼多多|美团|京东|百度|快手|小红书|滴滴|网易|小米|华为|Google|Meta|Apple|Amazon|Microsoft)"
        match = re.search(company_pattern, text)
        if match:
            state_machine.update_extracted_info("target_company", match.group(1))

        years_pattern = r"(\\d+(?:\\.\\d+)?)[\\s]*年[\\s]*经验"
        match = re.search(years_pattern, text)
        if match:
            state_machine.update_extracted_info("years", float(match.group(1)))

    def _generate_response(self, user_input: str, intent: IntentType, state_machine: NegotiationStateMachine, conversation_history: List[ConversationTurn]) -> DialogueResponse:
        current_phase = state_machine.current_phase

        if current_phase == NegotiationPhase.P1_INFO_GATHERING:
            return self._generate_info_gathering_response(user_input, intent, state_machine)
        elif current_phase == NegotiationPhase.P2_STRATEGY_FORMULATION:
            return self._generate_strategy_response(user_input, intent, state_machine)
        elif current_phase == NegotiationPhase.P3_PRACTICE_NEGOTIATION:
            return self._generate_roleplay_response(user_input, intent, state_machine)
        elif current_phase == NegotiationPhase.P4_DECISION_SUPPORT:
            return self._generate_decision_response(user_input, intent, state_machine)
        else:
            return self._generate_default_response(user_input, state_machine)

    def _generate_info_gathering_response(self, user_input: str, intent: IntentType, state_machine: NegotiationStateMachine) -> DialogueResponse:
        completeness = state_machine.check_info_completeness()
        missing_prompt = state_machine.get_missing_info_prompt()

        if missing_prompt:
            content = f"为了给你制定最合适的谈薪策略，我还需要了解以下信息：\\n\\n{missing_prompt}\\n\\n这些信息会直接影响你的谈判筹码和策略选择。"
            strategy = "信息收集"
        else:
            content = "信息收集完成！我已经了解了你的基本情况。现在我们可以进入策略制定阶段，你希望我帮你准备谈判策略吗？"
            strategy = "阶段推进"

        return DialogueResponse(
            content=content,
            phase=NegotiationPhase.P1_INFO_GATHERING,
            strategy=strategy,
            confidence=0.9,
            suggested_actions=["补充信息", "进入策略制定"] if not missing_prompt else []
        )

    def _generate_strategy_response(self, user_input: str, intent: IntentType, state_machine: NegotiationStateMachine) -> DialogueResponse:
        metadata = state_machine.user_metadata

        references = self.rag_retriever.retrieve(
            query=f"{metadata.target_company} {metadata.role} 薪资谈判策略",
            company=metadata.target_company,
            role=metadata.role
        )

        estimate = self.salary_estimator.estimate(
            company=metadata.target_company,
            role=metadata.role,
            years=metadata.years,
            education=metadata.education,
            level=metadata.target_level
        )

        leverages = self._analyze_leverages(metadata)
        opening_price = self._calculate_opening_price(metadata, estimate)

        content = f"""基于你的情况，我帮你梳理一下谈判策略：

**💡 你的筹码分析**：
{chr(10).join([f"• {lv}" for lv in leverages])}

**🎯 建议开口价**：base {opening_price}k（比你的期望上限高10-15%，留出谈判空间）

**📋 核心策略**：
1. **反问询价**：不要先报价，先问HR这个岗位的薪酬带宽是多少
2. **STAR价值陈述**：准备1-2个具体项目，说明你为什么值这个价
3. **对比筹码**：适当提及其他offer作为锚定，但不要过度施压
4. **替代补偿**：如果base谈不动，争取签字费、股票或更快归属

你现在处于策略制定阶段，需要我帮你准备具体的谈判话术吗？"""

        return DialogueResponse(
            content=content,
            phase=NegotiationPhase.P2_STRATEGY_FORMULATION,
            strategy="筹码分析+策略制定",
            confidence=0.88,
            suggested_actions=["准备话术", "模拟谈判", "薪资预估详情"],
            references=references[:3]
        )

    def _generate_roleplay_response(self, user_input: str, intent: IntentType, state_machine: NegotiationStateMachine) -> DialogueResponse:
        if "模拟" in user_input or "扮演" in user_input or "练" in user_input:
            content = self.strategy_library.get_pressure_test_scenario("budget_limit")
            strategy = "话术生成+风险提醒"
        else:
            content = self._generate_counter_response(user_input, state_machine)
            strategy = "应对策略"

        return DialogueResponse(
            content=content,
            phase=NegotiationPhase.P3_PRACTICE_NEGOTIATION,
            strategy=strategy,
            confidence=0.85,
            suggested_actions=["继续模拟", "换一个场景", "回到策略制定"]
        )

    def _generate_decision_response(self, user_input: str, intent: IntentType, state_machine: NegotiationStateMachine) -> DialogueResponse:
        offer_match = re.search(r"(?:base|薪资).*?(\\d+[\\.\\d]*)", user_input)
        offer_base = float(offer_match.group(1)) if offer_match else None

        expected_min = state_machine.user_metadata.expected_salary_min or 0
        expected_max = state_machine.user_metadata.expected_salary_max or 999

        if offer_base:
            if offer_base < expected_min * 0.9:
                assessment = "低于预期，建议再争取"
            elif offer_base < expected_min:
                assessment = "接近底线，可接受但仍有空间"
            elif offer_base <= expected_max:
                assessment = "符合预期，建议接受"
            else:
                assessment = "超出预期，强烈建议接受"

            content = f"""**📊 谈判结果评估：{assessment}**

HR坚持base {offer_base}k，这在你的期望区间内。

**🎯 你的选项**：
1. **接受**：如果平台或业务对你职业发展很重要
2. **再争取一次**：写邮件重申价值，看是否有特批空间
3. **拒绝**：如果你有更好的backup offer

**⚠️ 注意**：如果接受低于预期的package，下次跳槽的谈判基数会更低，形成薪资累积劣势。这是一个长期决策，不要只看眼前。"""
        else:
            content = "请告诉我HR最终给的数字，我帮你评估。"

        return DialogueResponse(
            content=content,
            phase=NegotiationPhase.P4_DECISION_SUPPORT,
            strategy="结果评估+决策建议",
            confidence=0.82,
            suggested_actions=["接受offer", "再争取一次", "拒绝并继续找"]
        )

    def _generate_default_response(self, user_input: str, state_machine: NegotiationStateMachine) -> DialogueResponse:
        return DialogueResponse(
            content=f"我理解你的需求。当前阶段：{state_machine.current_phase.value}。请告诉我更多细节，我可以更好地帮助你。",
            phase=state_machine.current_phase,
            strategy="默认回应",
            confidence=0.6
        )

    def _analyze_leverages(self, metadata: UserMetadata) -> List[str]:
        leverages = []
        if metadata.has_other_offer:
            leverages.append("手上有其他offer，可作为锚定筹码")
        if metadata.years >= 5:
            leverages.append(f"{metadata.years}年经验，具备资深背景")
        if "985" in metadata.education or "211" in metadata.education:
            leverages.append("学历背景优秀，具备溢价空间")
        if metadata.skills:
            leverages.append(f"技能稀缺性：{', '.join(metadata.skills[:3])}")
        if metadata.leverages:
            for lv in metadata.leverages:
                leverages.append(lv)
        if not leverages:
            leverages.append("应届生/初级经验，强调潜力和学习能力")
        return leverages

    def _calculate_opening_price(self, metadata: UserMetadata, estimate) -> int:
        if metadata.expected_salary_max:
            return int(metadata.expected_salary_max * 1.12)
        elif estimate and estimate.estimated_base:
            return int(estimate.estimated_base * 1.1)
        else:
            return 30

    def _generate_counter_response(self, user_input: str, state_machine: NegotiationStateMachine) -> str:
        if "低" in user_input or "预算" in user_input:
            return self.strategy_library.get_pressure_test_scenario("budget_limit")
        elif "其他offer" in user_input or "手上" in user_input:
            return self.strategy_library.get_pressure_test_scenario("anchor_trap")
        else:
            return "很好，这个回应方向是对的。你还可以补充..."

    def _create_error_response(self, message: str) -> DialogueResponse:
        return DialogueResponse(
            content=message,
            phase=NegotiationPhase.P1_INFO_GATHERING,
            strategy="错误处理",
            confidence=1.0
        )

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        session = self.sessions.get(session_id)
        if not session:
            return {}
        return {
            "session_id": session_id,
            "current_phase": session["state_machine"].current_phase.value,
            "turn_count": len(session["conversation_history"]) // 2,
            "user_metadata": session["user_metadata"].dict(),
            "state_summary": session["state_machine"].get_state_summary()
        }
'''

with open('/mnt/agents/output/salary_negotiation_agent/core/dialogue_engine.py', 'w', encoding='utf-8') as f:
    f.write(dialogue_engine_code)

print(" core/dialogue_engine.py")
