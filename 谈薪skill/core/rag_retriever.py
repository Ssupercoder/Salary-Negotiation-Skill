
# 8. core/rag_retriever.py
rag_retriever_code = '''"""
RAG检索模块
薪酬结构/公司政策/市场锚点向量库
"""
import random
from typing import Dict, Any, List, Optional
from models.schema import RAGDocument


class RAGRetriever:
    """RAG检索器"""

    def __init__(self, vector_db_path: str = "data/vector_db"):
        self.vector_db_path = vector_db_path
        self.documents: List[RAGDocument] = []
        self.embeddings: List[List[float]] = []
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        self.documents = [
            RAGDocument(
                doc_id="comp_pdd_001",
                content="拼多多视觉设计师T3-1级别：base 50k-75k，总包80-120万，16薪，签字费3-6万",
                doc_type="薪酬结构",
                company="拼多多",
                role="视觉设计师",
                source="OfferShow聚合数据"
            ),
            RAGDocument(
                doc_id="comp_pdd_002",
                content="拼多多薪资谈判特点：HR权限较大，可谈空间在base 10-15%，签字费弹性大",
                doc_type="公司政策",
                company="拼多多",
                source="内部经验分享"
            ),
            RAGDocument(
                doc_id="market_design_001",
                content="2026年互联网视觉设计师市场：7年经验base中位数65k，P6/T3-1级别主流区间55k-80k",
                doc_type="市场锚点",
                role="视觉设计师",
                source="行业薪酬报告"
            ),
            RAGDocument(
                doc_id="comp_google_001",
                content="Google中国视觉设计师：base 70k-85k，总包100-140万，15薪，签字费5-10万",
                doc_type="薪酬结构",
                company="Google",
                role="视觉设计师",
                source="OfferShow聚合数据"
            ),
            RAGDocument(
                doc_id="strategy_001",
                content="反问询价策略：不要先报价，先问HR岗位的薪酬带宽，让对方先暴露预算区间",
                doc_type="谈判案例",
                source="策略库"
            ),
            RAGDocument(
                doc_id="strategy_002",
                content="STAR价值陈述：Situation-Task-Action-Result，用具体项目证明价值",
                doc_type="谈判案例",
                source="策略库"
            ),
            RAGDocument(
                doc_id="comp_bytedance_001",
                content="字节跳动设计师2-1级别：base 35k-50k，2-2级别50k-70k，期权按级别递增",
                doc_type="薪酬结构",
                company="字节跳动",
                role="设计师",
                source="OfferShow聚合数据"
            ),
            RAGDocument(
                doc_id="policy_stock_001",
                content="互联网公司股票归属常见模式：4年归属，第一年0%，后三年每年33%；或4年每年25%",
                doc_type="公司政策",
                source="通用政策"
            ),
            RAGDocument(
                doc_id="market_2026_001",
                content="2026年互联网校招SP薪资：算法40k-50k，开发35k-45k，产品30k-40k，设计25k-35k",
                doc_type="市场锚点",
                source="校招薪酬报告"
            ),
            RAGDocument(
                doc_id="case_001",
                content="案例：7年经验设计师，双非本科，通过实习转正+其他offer锚定，最终base从65k谈到78k",
                doc_type="谈判案例",
                company="拼多多",
                role="视觉设计师",
                source="成功案例库"
            )
        ]
        random.seed(42)
        self.embeddings = [[random.random() for _ in range(128)] for _ in self.documents]

    def retrieve(self, query: str, company: Optional[str] = None, role: Optional[str] = None, doc_types: Optional[List[str]] = None, top_k: int = 5) -> List[RAGDocument]:
        candidates = self.documents
        if company:
            candidates = [d for d in candidates if d.company == company or d.company is None]
        if role:
            candidates = [d for d in candidates if d.role == role or d.role is None]
        if doc_types:
            candidates = [d for d in candidates if d.doc_type in doc_types]

        scored_docs = []
        for doc in candidates:
            score = self._calculate_similarity(query, doc)
            scored_docs.append((doc, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        results = []
        for doc, score in scored_docs[:top_k]:
            doc.score = score
            results.append(doc)
        return results

    def _calculate_similarity(self, query: str, doc: RAGDocument) -> float:
        score = 0.0
        query_lower = query.lower()
        content_lower = doc.content.lower()
        if doc.company and doc.company.lower() in query_lower:
            score += 0.4
        if doc.role and doc.role.lower() in query_lower:
            score += 0.3
        keywords = query_lower.split()
        for kw in keywords:
            if len(kw) > 2 and kw in content_lower:
                score += 0.1
        if doc.doc_type == "薪酬结构":
            score *= 1.2
        elif doc.doc_type == "谈判案例":
            score *= 1.1
        return min(score, 1.0)

    def add_document(self, doc: RAGDocument):
        self.documents.append(doc)
        self.embeddings.append([random.random() for _ in range(128)])

    def get_company_salary_info(self, company: str, role: str) -> Optional[Dict[str, Any]]:
        docs = self.retrieve(query=f"{company} {role} 薪资", company=company, role=role, doc_types=["薪酬结构"], top_k=3)
        if not docs:
            return None
        return {"company": company, "role": role, "references": [doc.content for doc in docs], "source_count": len(docs)}

    def get_market_anchor(self, role: str, years: float) -> Optional[Dict[str, Any]]:
        docs = self.retrieve(query=f"{role} {years}年 市场薪资", role=role, doc_types=["市场锚点"], top_k=3)
        if not docs:
            return None
        return {"role": role, "years": years, "references": [doc.content for doc in docs]}
'''

with open('/mnt/agents/output/salary_negotiation_agent/core/rag_retriever.py', 'w', encoding='utf-8') as f:
    f.write(rag_retriever_code)

print(" core/rag_retriever.py")

