# 2. models/schema.py
schema_code = '''"""
谈薪Agent数据模型定义
对应JSONL数据格式和系统内部状态管理
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class EducationLevel(str, Enum):
    """教育背景枚举"""
    HIGH_SCHOOL = "高中"
    ASSOCIATE = "大专"
    BACHELOR = "本科"
    MASTER = "硕士"
    PHD = "博士"
    UNKNOWN = "未知"


class NegotiationPhase(str, Enum):
    """谈薪五阶段"""
    P1_INFO_GATHERING = "P1_信息收集"
    P2_STRATEGY_FORMULATION = "P2_策略制定"
    P3_PRACTICE_NEGOTIATION = "P3_实战谈判"
    P4_DECISION_SUPPORT = "P4_决策辅助"
    P5_POST_NEGOTIATION = "P5_后续跟进"


class SpeakerRole(str, Enum):
    """对话角色"""
    USER = "human"
    AGENT = "gpt"


class LeverageType(str, Enum):
    """谈判筹码类型"""
    OTHER_OFFER = "其他offer"
    EDUCATION_PREMIUM = "学历溢价"
    SKILL_SCARCITY = "技能稀缺性"
    INTERNSHIP_CONVERSION = "实习转正"
    CORE_PROJECT = "核心项目经验"
    TEAM_LEAD = "带团队经验"
    MARKET_ANCHOR = "市场锚定价"
    CAREER_TRAJECTORY = "职业发展轨迹"


class ConversationTurn(BaseModel):
    """单轮对话记录"""
    from_: SpeakerRole = Field(..., alias="from")
    value: str = Field(..., description="对话内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="轮次元数据")

    class Config:
        populate_by_name = True


class UserMetadata(BaseModel):
    """用户背景元数据"""
    target_company: str = Field(..., description="目标公司")
    role: str = Field(..., description="目标岗位")
    years: Union[int, float] = Field(..., description="工作年限")
    education: str = Field(..., description="教育背景")
    has_other_offer: bool = Field(default=False, description="是否有其他offer")
    leverages: List[str] = Field(default_factory=list, description="谈判筹码列表")
    phases_covered: List[str] = Field(default_factory=list, description="已覆盖阶段")

    current_company: Optional[str] = Field(None, description="当前/最近公司")
    current_salary: Optional[float] = Field(None, description="当前薪资(base)")
    expected_salary_min: Optional[float] = Field(None, description="期望薪资下限")
    expected_salary_max: Optional[float] = Field(None, description="期望薪资上限")
    target_level: Optional[str] = Field(None, description="目标职级")
    skills: List[str] = Field(default_factory=list, description="技能标签")
    project_scale: Optional[str] = Field(None, description="项目量级")
    is_new_grad: bool = Field(default=False, description="是否应届生")
    deadline: Optional[str] = Field(None, description="HR确认deadline")
    other_offers: List[Dict[str, Any]] = Field(default_factory=list, description="其他offer详情")


class SalaryNegotiationRecord(BaseModel):
    """单条谈薪数据记录（对应JSONL一行）"""
    id: str = Field(..., description="记录ID")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: UserMetadata = Field(..., description="用户背景信息")
    conversations: List[ConversationTurn] = Field(default_factory=list, description="对话历史")

    current_phase: NegotiationPhase = Field(default=NegotiationPhase.P1_INFO_GATHERING)
    extracted_info: Dict[str, Any] = Field(default_factory=dict, description="已提取信息")
    strategy_plan: Optional[Dict[str, Any]] = Field(None, description="策略方案")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class IntentType(str, Enum):
    """用户意图类型"""
    INFO_PROVIDE = "信息提供"
    INFO_QUERY = "信息查询"
    STRATEGY_REQUEST = "策略请求"
    ROLE_PLAY = "角色扮演"
    OFFER_EVALUATION = "offer评估"
    DECISION_HELP = "决策帮助"
    CHITCHAT = "闲聊"
    UNKNOWN = "未知"


class StrategyTemplate(BaseModel):
    """策略模板"""
    name: str
    description: str
    applicable_phases: List[NegotiationPhase]
    prompt_template: str
    example_responses: List[str] = Field(default_factory=list)


class RAGDocument(BaseModel):
    """RAG检索文档"""
    doc_id: str
    content: str
    doc_type: str
    company: Optional[str] = None
    role: Optional[str] = None
    source: str
    score: float = 0.0


class SalaryEstimate(BaseModel):
    """薪资预估结果"""
    company: str
    role: str
    level: Optional[str] = None
    estimated_base: float
    estimated_total: float
    confidence: float
    reference_range: tuple
    data_sources: List[str] = Field(default_factory=list)
    notes: str = ""


class DialogueResponse(BaseModel):
    """Agent回复结构"""
    content: str
    phase: NegotiationPhase
    strategy: str
    confidence: float
    suggested_actions: List[str] = Field(default_factory=list)
    risk_warnings: List[str] = Field(default_factory=list)
    references: List[RAGDocument] = Field(default_factory=list)
'''

with open('/mnt/agents/output/salary_negotiation_agent/models/schema.py', 'w', encoding='utf-8') as f:
    f.write(schema_code)

print(" models/schema.py")
