
# 15. config.py
config_code = '''"""
系统配置
"""

# 模型配置
MODEL_CONFIG = {
    "core_llm": "Qwen/Qwen2.5-7B-Instruct",
    "use_vllm": True,
    "quantization": "INT8",
    "max_tokens": 2048,
    "temperature": 0.7,
    "top_p": 0.9
}

# 轻量模型配置（意图识别）
LIGHT_MODEL_CONFIG = {
    "model": "intent-classifier-0.5b",
    "max_length": 512,
    "device": "cuda"
}

# 多模态配置
MULTIMODAL_CONFIG = {
    "pdf": {
        "engine": "PaddleOCR",
        "use_angle_cls": True,
        "lang": "ch",
        "needs_manual_confirm": True
    },
    "audio": {
        "model": "openai/whisper-base",
        "sampling_rate": 16000,
        "language": "zh"
    }
}

# RAG配置
RAG_CONFIG = {
    "vector_db": "faiss",
    "embedding_model": "BAAI/bge-large-zh-v1.5",
    "top_k": 5,
    "score_threshold": 0.6,
    "chunk_size": 512,
    "chunk_overlap": 128
}

# 状态机配置
STATE_MACHINE_CONFIG = {
    "phases": [
        "P1_信息收集",
        "P2_策略制定",
        "P3_实战谈判",
        "P4_决策辅助",
        "P5_后续跟进"
    ],
    "max_turns_per_phase": 10,
    "auto_advance": True
}

# 安全过滤配置
SAFETY_CONFIG = {
    "enable_input_filter": True,
    "enable_output_filter": True,
    "sensitive_word_categories": [
        "political", "illegal", "discrimination",
        "privacy", "malicious_competition"
    ],
    "block_level": ["HIGH", "CRITICAL"],
    "warn_level": ["LOW", "MEDIUM"]
}

# 评估配置
EVAL_CONFIG = {
    "metrics": ["latency", "rouge", "bleu", "satisfaction"],
    "latency_budget_ms": 2000,
    "satisfaction_threshold": 4.0
}

# 薪资预估配置
SALARY_ESTIMATE_CONFIG = {
    "default_sp_base": 35,
    "data_sources": ["OfferShow", "脉脉", "内部数据"],
    "confidence_threshold": 0.7
}

# 存储配置
STORAGE_CONFIG = {
    "session_db": "sqlite:///data/sessions.db",
    "conversation_log": "data/conversations.jsonl",
    "knowledge_base": "data/knowledge_base/"
}
'''

with open('/mnt/agents/output/salary_negotiation_agent/config.py', 'w', encoding='utf-8') as f:
    f.write(config_code)

print(" config.py")
