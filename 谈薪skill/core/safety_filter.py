
# 10. core/safety_filter.py
safety_filter_code = '''"""
安全过滤模块
规则引擎 + 敏感词库 + 二次校验
"""
import re
from typing import Dict, Any, List
from enum import Enum


class RiskLevel(str, Enum):
    """风险等级"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafetyFilter:
    """安全过滤器"""

    def __init__(self):
        self.sensitive_words = {
            "political": ["反动", "颠覆", "政权", "暴乱", "分裂", "独立", "游行", "示威", "集会", "煽动"],
            "illegal": ["诈骗", "洗钱", "贿赂", "回扣", "造假", "伪造", "偷税", "漏税", "非法集资", "传销"],
            "discrimination": ["性别歧视", "地域歧视", "种族歧视", "年龄歧视", "残疾人", "同性恋", "异性恋"],
            "privacy": ["身份证号", "银行卡号", "密码", "家庭住址", "手机号", "邮箱", "具体住址"],
            "malicious_competition": ["挖角", "撬客户", "商业机密", "竞业协议", "保密协议"]
        }

        self.rules = [
            {"name": "隐私信息泄露", "pattern": r"\\d{17}[\\dXx]|\\d{4}\\d{4}\\d{4}\\d{4}", "risk_level": RiskLevel.HIGH, "action": "block"},
            {"name": "极端薪资要求", "pattern": r"(?:要求|必须|一定).*?(?:翻倍|三倍|五倍|十倍)", "risk_level": RiskLevel.LOW, "action": "warn"},
            {"name": "威胁性语言", "pattern": r"(?:不给我|否则|不然).*?(?:曝光|举报|投诉|媒体)", "risk_level": RiskLevel.MEDIUM, "action": "warn"},
            {"name": "虚假offer声明", "pattern": r"(?:伪造|假|虚构).*?offer", "risk_level": RiskLevel.HIGH, "action": "block"}
        ]

    def filter(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        violations = []
        violations.extend(self._check_sensitive_words(text))
        violations.extend(self._check_rules(text))
        if context:
            violations.extend(self._check_context(text, context))

        if not violations:
            return {"is_safe": True, "risk_level": RiskLevel.SAFE, "violations": [], "suggested_action": "pass", "filtered_text": text}

        max_risk = max(v["risk_level"] for v in violations)
        has_block = any(v["action"] == "block" for v in violations)
        filtered_text = self._filter_text(text, violations) if has_block else text

        return {
            "is_safe": max_risk not in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            "risk_level": max_risk,
            "violations": violations,
            "suggested_action": "block" if has_block else "warn",
            "filtered_text": filtered_text
        }

    def _check_sensitive_words(self, text: str) -> List[Dict[str, Any]]:
        violations = []
        text_lower = text.lower()
        for category, words in self.sensitive_words.items():
            for word in words:
                if word in text or word in text_lower:
                    violations.append({
                        "type": "sensitive_word", "category": category, "word": word,
                        "risk_level": RiskLevel.MEDIUM if category in ["privacy", "malicious_competition"] else RiskLevel.HIGH,
                        "action": "warn" if category in ["privacy"] else "block",
                        "message": f"检测到敏感词：{word}（类别：{category}）"
                    })
        return violations

    def _check_rules(self, text: str) -> List[Dict[str, Any]]:
        violations = []
        for rule in self.rules:
            if re.search(rule["pattern"], text, re.IGNORECASE):
                violations.append({
                    "type": "rule_violation", "rule_name": rule["name"],
                    "risk_level": rule["risk_level"], "action": rule["action"],
                    "message": f"触发规则：{rule['name']}"
                })
        return violations

    def _check_context(self, text: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations = []
        if "other_people" in context:
            violations.append({"type": "context_violation", "category": "third_party_privacy", "risk_level": RiskLevel.MEDIUM, "action": "warn", "message": "涉及第三方个人信息，请注意隐私保护"})
        if "encourage_illegal" in context:
            violations.append({"type": "context_violation", "category": "illegal_encouragement", "risk_level": RiskLevel.CRITICAL, "action": "block", "message": "检测到鼓励违法行为的内容"})
        return violations

    def _filter_text(self, text: str, violations: List[Dict]) -> str:
        filtered = text
        for v in violations:
            if v["type"] == "sensitive_word":
                word = v["word"]
                filtered = filtered.replace(word, "*" * len(word))
        return filtered

    def check_output_safety(self, output_text: str) -> Dict[str, Any]:
        harmful_patterns = [
            r"(?:伪造|虚构|编造).*?(?:经历|项目|数据|offer)",
            r"(?:威胁|恐吓|逼迫).*?HR",
            r"(?:泄露|公开|曝光).*?(?:公司机密|内部信息)"
        ]
        for pattern in harmful_patterns:
            if re.search(pattern, output_text, re.IGNORECASE):
                return {"is_safe": False, "risk_level": RiskLevel.HIGH, "action": "regenerate", "message": "输出包含潜在有害建议，需要重新生成"}
        return {"is_safe": True, "risk_level": RiskLevel.SAFE, "action": "pass"}

    def add_custom_rule(self, name: str, pattern: str, risk_level: RiskLevel, action: str):
        self.rules.append({"name": name, "pattern": pattern, "risk_level": risk_level, "action": action})
'''

with open('/mnt/agents/output/salary_negotiation_agent/core/safety_filter.py', 'w', encoding='utf-8') as f:
    f.write(safety_filter_code)

print(" core/safety_filter.py")

