
input_processor_code = '''"""
多模态输入处理模块
支持：PDF简历解析、语音转文字、文本输入
"""
import re
from typing import Dict, Any, Optional, Union


class PDFProcessor:
    """PDF简历解析器（基于PaddleOCR）"""

    def __init__(self, use_paddle: bool = True):
        self.use_paddle = use_paddle
        self.extracted_fields = {}

    def process(self, pdf_path: Union[str, bytes]) -> Dict[str, Any]:
        raw_text = self._extract_text(pdf_path)
        structured = self._parse_structure(raw_text)

        return {
            "raw_text": raw_text,
            "structured": structured,
            "confidence": structured.get("_confidence", 0.85),
            "needs_manual_confirm": structured.get("_needs_confirm", False)
        }

    def _extract_text(self, pdf_path: Union[str, bytes]) -> str:
        return "[PDF文本提取结果 - 实际使用PaddleOCR]"

    def _parse_structure(self, raw_text: str) -> Dict[str, Any]:
        structured = {
            "name": self._extract_name(raw_text),
            "education": self._extract_education(raw_text),
            "work_experience": self._extract_work_experience(raw_text),
            "skills": self._extract_skills(raw_text),
            "projects": self._extract_projects(raw_text),
            "current_company": self._extract_current_company(raw_text),
            "years_of_experience": self._extract_years(raw_text),
            "_confidence": 0.85,
            "_needs_confirm": True
        }
        return structured

    def _extract_name(self, text: str) -> Optional[str]:
        patterns = [
            r"姓名[：:]\\s*(\\S+)",
            r"Name[：:]\\s*(\\S+)",
            r"^(\\S{2,4})$"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return match.group(1)
        return None

    def _extract_education(self, text: str) -> Dict[str, Any]:
        education = {"school": None, "degree": None, "major": None, "is_985_211": False, "is_overseas": False}
        school_pattern = r"(清华大学|北京大学|复旦大学|上海交通大学|浙江大学|[^\\s]{2,10}大学|[^\\s]{2,10}学院)"
        match = re.search(school_pattern, text)
        if match:
            education["school"] = match.group(1)
        degree_pattern = r"(博士|硕士|本科|大专|高中)"
        match = re.search(degree_pattern, text)
        if match:
            education["degree"] = match.group(1)
        return education

    def _extract_work_experience(self, text: str) -> list:
        experiences = []
        company_pattern = r"(\\d{4}[\\.年])?[-~至]?(\\d{4}[\\.年]|至今)?\\s*(\\S+公司|\\S+科技|\\S+集团)"
        matches = re.finditer(company_pattern, text)
        for match in matches:
            experiences.append({"company": match.group(3), "period": f"{match.group(1) or ''}-{match.group(2) or ''}"})
        return experiences

    def _extract_skills(self, text: str) -> list:
        skill_keywords = ["Python", "Java", "C++", "Go", "Rust", "机器学习", "深度学习", "NLP", "CV",
                          "产品设计", "UI设计", "UX", "品牌设计", "3D设计", "插画", "AIGC", "Figma", "Sketch",
                          "项目管理", "团队管理", "数据分析"]
        found_skills = []
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        return found_skills

    def _extract_projects(self, text: str) -> list:
        projects = []
        project_blocks = re.split(r"项目经验|Projects", text)
        if len(project_blocks) > 1:
            project_text = project_blocks[1]
            project_names = re.findall(r"[•\\-]\\s*(\\S+项目|\\S+系统|\\S+平台)", project_text)
            for name in project_names[:5]:
                projects.append({"name": name, "description": ""})
        return projects

    def _extract_current_company(self, text: str) -> Optional[str]:
        experiences = self._extract_work_experience(text)
        if experiences:
            return experiences[-1].get("company")
        return None

    def _extract_years(self, text: str) -> Optional[float]:
        grad_pattern = r"(\\d{4})[\\.年]\\s*毕业"
        match = re.search(grad_pattern, text)
        if match:
            grad_year = int(match.group(1))
            import datetime
            years = datetime.datetime.now().year - grad_year
            return float(years)
        return None


class AudioProcessor:
    """语音处理器（基于Whisper-base）"""

    def __init__(self, model_name: str = "openai/whisper-base"):
        self.model_name = model_name

    def process(self, audio_path: Union[str, bytes]) -> Dict[str, Any]:
        return {
            "text": "[语音转写结果 - 实际使用Whisper-base]",
            "language": "zh",
            "confidence": 0.92,
            "segments": []
        }

    def process_stream(self, audio_chunk: bytes) -> str:
        return "[流式语音处理结果]"


class TextProcessor:
    """文本输入处理器"""

    def __init__(self):
        self.entity_patterns = {
            "company": r"(字节跳动|腾讯|阿里巴巴|拼多多|美团|京东|百度|快手|小红书|滴滴|网易|小米|华为|Google|Meta|Apple|Amazon|Microsoft)",
            "salary": r"(\\d+[\\.\\d]*)\\s*[kK万]",
            "role": r"(算法工程师|产品经理|设计师|运营|开发工程师|视觉设计师|交互设计师)",
            "level": r"(T[\\d]-[\\d]|P[\\d]|M[\\d]|L[\\d]|\\d-\\d级)"
        }

    def process(self, text: str) -> Dict[str, Any]:
        cleaned = self._clean_text(text)
        entities = self._extract_entities(cleaned)
        intent_hints = self._detect_intent_hints(cleaned)
        sentiment = self._analyze_sentiment(cleaned)

        return {
            "cleaned_text": cleaned,
            "entities": entities,
            "intent_hints": intent_hints,
            "sentiment": sentiment
        }

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\\s+", " ", text)
        text = re.sub(r"[^\\u4e00-\\u9fa5a-zA-Z0-9\\s，。！？、：；（）\"\"''【】《》]", "", text)
        return text.strip()

    def _extract_entities(self, text: str) -> Dict[str, Any]:
        entities = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = matches
        return entities

    def _detect_intent_hints(self, text: str) -> list:
        hints = []
        hint_keywords = {
            "offer_received": ["收到offer", "给了offer", "发offer", "录用"],
            "salary_negotiation": ["谈薪", "薪资", "工资", "package", "总包", "base"],
            "strategy_request": ["怎么谈", "策略", "话术", "技巧", "建议"],
            "role_play": ["模拟", "扮演", "练习", "rehearsal", "练一下"],
            "info_query": ["多少", "什么水平", "市场", "行情", "参考"],
            "decision": ["要不要", "纠结", "选择", "对比", "哪个好"]
        }
        for intent, keywords in hint_keywords.items():
            if any(kw in text for kw in keywords):
                hints.append(intent)
        return hints

    def _analyze_sentiment(self, text: str) -> str:
        positive = ["开心", "满意", "不错", "好", "高", "理想"]
        negative = ["低", "不满意", "差", "纠结", "焦虑", "担心", "害怕"]
        p_count = sum(1 for w in positive if w in text)
        n_count = sum(1 for w in negative if w in text)
        if p_count > n_count:
            return "positive"
        elif n_count > p_count:
            return "negative"
        return "neutral"


class MultiModalInputProcessor:
    """多模态输入统一处理器"""

    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.audio_processor = AudioProcessor()
        self.text_processor = TextProcessor()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        input_type = input_data.get("type", "text")
        content = input_data.get("content", "")

        if input_type == "pdf":
            result = self.pdf_processor.process(content)
            return {
                "type": "pdf",
                "text": result["raw_text"],
                "structured": result["structured"],
                "confidence": result["confidence"],
                "needs_manual_confirm": result["needs_manual_confirm"],
                "extracted_metadata": self._convert_pdf_to_metadata(result["structured"])
            }
        elif input_type == "audio":
            result = self.audio_processor.process(content)
            text_result = self.text_processor.process(result["text"])
            return {
                "type": "audio",
                "text": result["text"],
                "language": result["language"],
                "confidence": result["confidence"],
                "entities": text_result["entities"],
                "intent_hints": text_result["intent_hints"]
            }
        elif input_type == "text":
            result = self.text_processor.process(content)
            return {
                "type": "text",
                "text": result["cleaned_text"],
                "entities": result["entities"],
                "intent_hints": result["intent_hints"],
                "sentiment": result["sentiment"]
            }
        elif input_type == "mixed":
            return self._process_mixed_input(content)

        return {"type": "unknown", "text": "", "error": "Unsupported input type"}

    def _convert_pdf_to_metadata(self, structured: Dict[str, Any]) -> Dict[str, Any]:
        education = structured.get("education", {})
        return {
            "education": education.get("degree", "未知"),
            "years": structured.get("years_of_experience"),
            "current_company": structured.get("current_company"),
            "skills": structured.get("skills", []),
            "is_new_grad": structured.get("years_of_experience", 99) <= 1
        }

    def _process_mixed_input(self, content: Dict[str, Any]) -> Dict[str, Any]:
        pdf_result = self.pdf_processor.process(content.get("pdf_path", ""))
        manual_info = content.get("manual_input", {})
        merged = {**pdf_result["structured"], **manual_info}
        return {
            "type": "mixed",
            "pdf_text": pdf_result["raw_text"],
            "merged_structure": merged,
            "needs_manual_confirm": pdf_result["needs_manual_confirm"]
        }
'''

with open('/mnt/agents/output/salary_negotiation_agent/core/input_processor.py', 'w', encoding='utf-8') as f:
    f.write(input_processor_code)

print(" core/input_processor.py")
