"""
JSONL数据加载与处理
"""
import json
from pathlib import Path
from typing import Iterator, List
from models.schema import SalaryNegotiationRecord


class JSONLDataLoader:
    """JSONL数据加载器"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def load(self) -> Iterator[SalaryNegotiationRecord]:
        """逐条加载数据"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    yield SalaryNegotiationRecord(**data)

    def load_all(self) -> List[SalaryNegotiationRecord]:
        """加载全部数据"""
        return list(self.load())

    def save(self, record: SalaryNegotiationRecord, append: bool = True):
        """保存单条记录"""
        mode = 'a' if append else 'w'
        with open(self.file_path, mode, encoding='utf-8') as f:
            f.write(record.model_dump_json() + '\n')

    def get_statistics(self) -> dict:
        """数据统计"""
        records = self.load_all()
        phases = {}
        companies = {}
        roles = {}

        for r in records:
            for conv in r.conversations:
                phase = conv.metadata.get("phase", "unknown")
                phases[phase] = phases.get(phase, 0) + 1

            companies[r.metadata.target_company] = companies.get(r.metadata.target_company, 0) + 1
            roles[r.metadata.role] = roles.get(r.metadata.role, 0) + 1

        return {
            "total_records": len(records),
            "phase_distribution": phases,
            "company_distribution": companies,
            "role_distribution": roles
        }


# 使用示例
if __name__ == "__main__":
    loader = JSONLDataLoader("data/salary_negotiation_500_samples.jsonl")

    # 加载并统计
    stats = loader.get_statistics()
    print(f"总记录数: {stats['total_records']}")
    print(f"阶段分布: {stats['phase_distribution']}")