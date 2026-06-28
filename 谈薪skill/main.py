"""
谈薪Skill Agent主程序
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from models.schema import UserMetadata, SalaryNegotiationRecord, NegotiationPhase
from models.state_machine import NegotiationStateMachine
from core.input_processor import MultiModalInputProcessor
from core.dialogue_engine import DialogueEngine
from core.safety_filter import SafetyFilter
from evaluation.metrics import MetricsCalculator, LatencyTracker


class SalaryNegotiationAgent:
    """谈薪智能Agent主类"""

    def __init__(self):
        self.input_processor = MultiModalInputProcessor()
        self.dialogue_engine = DialogueEngine()
        self.safety_filter = SafetyFilter()
        self.metrics = MetricsCalculator()

    def create_session(self, user_info: Dict[str, Any]) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())

        metadata = UserMetadata(
            target_company=user_info.get("target_company", ""),
            role=user_info.get("role", ""),
            years=user_info.get("years", 0),
            education=user_info.get("education", "本科"),
            has_other_offer=user_info.get("has_other_offer", False),
            leverages=user_info.get("leverages", []),
            current_company=user_info.get("current_company"),
            current_salary=user_info.get("current_salary"),
            expected_salary_min=user_info.get("expected_salary_min"),
            expected_salary_max=user_info.get("expected_salary_max"),
            target_level=user_info.get("target_level"),
            skills=user_info.get("skills", []),
            is_new_grad=user_info.get("is_new_grad", False)
        )

        self.dialogue_engine.initialize_session(session_id, metadata)
        return session_id

    def process_input(self, session_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理用户输入并返回回复
        """
        # 1. 多模态输入处理
        processed = self.input_processor.process(input_data)

        # 2. 安全过滤（输入）
        text_content = processed.get("text", "")
        safety_result = self.safety_filter.filter(text_content)

        if not safety_result["is_safe"]:
            return {
                "success": False,
                "content": "输入内容包含敏感信息，请调整后重试。",
                "risk_level": safety_result["risk_level"].value,
                "violations": safety_result["violations"]
            }

        # 3. 核心对话处理（带延迟追踪）
        with LatencyTracker(self.metrics) as tracker:
            response = self.dialogue_engine.process_turn(
                session_id=session_id,
                user_input=text_content,
                input_type=processed.get("type", "text")
            )
            tracker.mark("llm_generation")

        # 4. 安全过滤（输出）
        output_safety = self.safety_filter.check_output_safety(response.content)
        if not output_safety["is_safe"]:
            return {
                "success": False,
                "content": "生成内容需要调整，请重试。",
                "risk_level": output_safety["risk_level"].value
            }

        # 5. 构建返回
        return {
            "success": True,
            "content": response.content,
            "phase": response.phase.value,
            "strategy": response.strategy,
            "confidence": response.confidence,
            "suggested_actions": response.suggested_actions,
            "risk_warnings": response.risk_warnings,
            "references": [
                {
                    "content": ref.content,
                    "doc_type": ref.doc_type,
                    "source": ref.source,
                    "score": ref.score
                }
                for ref in response.references
            ]
        }

    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """获取会话状态"""
        return self.dialogue_engine.get_session_summary(session_id)

    def export_conversation(self, session_id: str) -> Optional[SalaryNegotiationRecord]:
        """导出对话记录为JSONL格式"""
        session = self.dialogue_engine.sessions.get(session_id)
        if not session:
            return None

        return SalaryNegotiationRecord(
            id=f"salary_negotiation_{session_id[:8]}",
            timestamp=datetime.now(),
            metadata=session["user_metadata"],
            conversations=session["conversation_history"],
            current_phase=session["state_machine"].current_phase
        )

    def get_metrics_report(self) -> Dict[str, Any]:
        """获取评估报告"""
        return self.metrics.generate_report()


# FastAPI服务入口（可选）
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="谈薪Skill Agent")
agent = SalaryNegotiationAgent()

class UserInputRequest(BaseModel):
    session_id: Optional[str] = None
    type: str = "text"
    content: str
    user_info: Optional[Dict] = None

@app.post("/chat")
async def chat(request: UserInputRequest):
    if not request.session_id:
        if not request.user_info:
            raise HTTPException(status_code=400, detail="新会话需要提供user_info")
        session_id = agent.create_session(request.user_info)
    else:
        session_id = request.session_id

    input_data = {
        "type": request.type,
        "content": request.content
    }

    response = agent.process_input(session_id, input_data)
    return {
        "session_id": session_id,
        **response
    }

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    state = agent.get_session_state(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="会话不存在")
    return state

@app.get("/metrics")
async def get_metrics():
    return agent.get_metrics_report()
"""


if __name__ == "__main__":
    # 示例运行
    agent = SalaryNegotiationAgent()

    # 创建会话
    user_info = {
        "target_company": "拼多多",
        "role": "视觉设计师",
        "years": 7,
        "education": "双非本科",
        "has_other_offer": True,
        "leverages": ["实习转正", "学历溢价"],
        "expected_salary_min": 65,
        "expected_salary_max": 80,
        "skills": ["插画", "3D设计", "品牌设计", "AIGC辅助设计"]
    }

    session_id = agent.create_session(user_info)
    print(f"会话已创建: {session_id}")

    # 模拟对话
    inputs = [
        "拼多多给我发offer了，但是薪资还没定，想请教怎么谈。",
        "补充一下：期望薪资base 65k-80k，有其他offer Google中国 base 75k，级别还没明确，HR说这周要给答复",
        "我想模拟一下谈判过程，你能扮演HR跟我练一下吗？",
        "今天谈完了。HR坚持说预算有限，base只能71k，没有谈判空间了。我现在有点不确定，你能帮我分析一下吗？"
    ]

    for user_input in inputs:
        print(f"\n{'='*50}")
        print(f"用户: {user_input}")
        result = agent.process_input(session_id, {"type": "text", "content": user_input})
        print(f"Agent: {result['content'][:200]}...")
        print(f"阶段: {result['phase']} | 策略: {result['strategy']}")