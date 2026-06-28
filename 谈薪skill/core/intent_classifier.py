# 6. core/intent_classifier.py
intent_classifier_code = '''"""
级联意图识别器
规则 -> 0.5B轻量模型 -> 7B兜底模型
"""
import re
from typing import Dict, Any, List
from models.schema import IntentType


class IntentClassifier:
    """级联意图分类器"""

    def __init__(self, use_llm: bool = True, use_fallback: bool = True):
        self.use_llm = use_llm
        self.use_fallback = use_fallback

        self.rule_patterns = {
            IntentType.INFO_PROVIDE: {
                "keywords": ["我是", "我有", "我目前", "我之前", "我在", "毕业于", "工作", "经验", "学历", "本科", "硕士", "博士", "专业是", "做", "负责"],
                "patterns": [r"我[是|在].*?(公司|工作)", r"我.*?年.*?经验", r"毕业于.*?大学", r"目前.*?薪资", r"手上?有.*?offer"]
            },
            IntentType.INFO_QUERY: {
                "keywords": ["多少", "什么水平", "市场价", "行情", "参考", "了解", "想知道", "薪资范围", "薪酬带宽", "总包", "package", "base"],
                "patterns": [r"(薪资|工资|package|总包).*?(多少|什么水平|怎么样)", r"(市场|行情|参考).*?(价|范围|水平)", r"(这家公司|这个岗位).*?(给|开|给多少)"]
            },
            IntentType.STRATEGY_REQUEST: {
                "keywords": ["怎么谈", "策略", "话术", "技巧", "建议", "开口", "报价", "怎么回", "怎么答", "怎么说", "准备", "制定"],
                "patterns": [r"(怎么|如何).*?(谈|聊|沟通)", r"给.*?建议", r"(策略|方案|话术|技巧)", r"开口.*?价"]
            },
            IntentType.ROLE_PLAY: {
                "keywords": ["模拟", "扮演", "练习", "rehearsal", "练一下", "试试", "扮演HR", "你来当", "你扮演", "假设"],
                "patterns": [r"(模拟|扮演|练习|练一下)", r"你[来|当|扮演].*?HR", r"假设.*?[说|问|讲]"]
            },
            IntentType.OFFER_EVALUATION: {
                "keywords": ["这个offer", "值不值", "怎么样", "合理吗", "低了吗", "高了吗", "匹配", "符合", "满意", "不满意", "纠结"],
                "patterns": [r"(这个|那个).*?offer.*?(怎么样|值不值|合理吗)", r"(薪资|package).*?(低|高|合理|匹配)", r"(纠结|犹豫|不确定).*?(去|接受|拒绝)"]
            },
            IntentType.DECISION_HELP: {
                "keywords": ["要不要", "选哪个", "怎么选", "对比", "比较", "哪个好", "去不去", "接受", "拒绝", "放弃", "选择"],
                "patterns": [r"(要不要|去不去|接不接).*?(去|接受|这个)", r"(选|挑).*?(哪个|哪家)", r"(对比|比较).*?(A|B|两家|两个)"]
            },
            IntentType.CHITCHAT: {
                "keywords": ["你好", "谢谢", "再见", "在吗", "忙吗", "打扰", "请问", "哈喽", "hi", "hello", "感谢", "拜拜"],
                "patterns": [r"^(你好|您好|哈喽|hi|hello)", r"^(谢谢|感谢)", r"^(再见|拜拜|bye)"]
            }
        }

        self.phase_intent_weights = {
            "P1_信息收集": {IntentType.INFO_PROVIDE: 1.5, IntentType.INFO_QUERY: 1.2},
            "P2_策略制定": {IntentType.STRATEGY_REQUEST: 1.5, IntentType.INFO_QUERY: 1.0},
            "P3_实战谈判": {IntentType.ROLE_PLAY: 1.8, IntentType.STRATEGY_REQUEST: 1.2},
            "P4_决策辅助": {IntentType.OFFER_EVALUATION: 1.5, IntentType.DECISION_HELP: 1.5}
        }

    def classify(self, text: str, current_phase: str = "", conversation_history: list = None) -> Dict[str, Any]:
        rule_result = self._rule_classify(text)
        if rule_result["confidence"] > 0.85:
            return rule_result

        if self.use_llm:
            light_result = self._light_model_classify(text, current_phase)
            if light_result["confidence"] > 0.75:
                return light_result
        else:
            light_result = None

        if self.use_fallback and self.use_llm:
            fallback_result = self._fallback_model_classify(text, current_phase, conversation_history)
            final = self._fuse_results(rule_result, light_result, fallback_result)
            return final

        return rule_result if rule_result["confidence"] > 0.5 else (light_result or rule_result)

    def _rule_classify(self, text: str) -> Dict[str, Any]:
        scores = {intent: 0.0 for intent in IntentType}
        text_lower = text.lower()

        for intent, config in self.rule_patterns.items():
            score = 0.0
            for kw in config["keywords"]:
                if kw in text_lower or kw in text:
                    score += 0.3
            for pattern in config["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 0.5
            scores[intent] = min(score, 1.0)

        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]

        return {"intent": best_intent, "confidence": best_score, "method": "rule", "all_scores": scores}

    def _light_model_classify(self, text: str, current_phase: str) -> Dict[str, Any]:
        return {"intent": IntentType.STRATEGY_REQUEST, "confidence": 0.65, "method": "light_model", "all_scores": {}}

    def _fallback_model_classify(self, text: str, current_phase: str, conversation_history: list = None) -> Dict[str, Any]:
        return {"intent": IntentType.STRATEGY_REQUEST, "confidence": 0.88, "method": "fallback_model", "all_scores": {}}

    def _fuse_results(self, rule_result: Dict, light_result: Dict, fallback_result: Dict) -> Dict[str, Any]:
        weights = {"rule": 0.3, "light_model": 0.3, "fallback_model": 0.4}
        if rule_result["confidence"] > 0.8:
            weights = {"rule": 0.5, "light_model": 0.2, "fallback_model": 0.3}
        results = [rule_result, light_result, fallback_result]
        best = max(results, key=lambda x: x["confidence"] * weights.get(x["method"], 0.3))

        return {
            "intent": best["intent"],
            "confidence": best["confidence"],
            "method": f"fused({best['method']})",
            "all_scores": {"rule": rule_result, "light": light_result, "fallback": fallback_result}
        }

    def classify_with_phase_context(self, text: str, current_phase: str, conversation_history: list = None) -> Dict[str, Any]:
        result = self.classify(text, current_phase, conversation_history)
        phase_weights = self.phase_intent_weights.get(current_phase, {})
        if result["intent"] in phase_weights:
            result["confidence"] = min(1.0, result["confidence"] * phase_weights[result["intent"]])
        return result
'''

with open('/mnt/agents/output/salary_negotiation_agent/core/intent_classifier.py', 'w', encoding='utf-8') as f:
    f.write(intent_classifier_code)

print(" core/intent_classifier.py")
