"""RRF（Reciprocal Rank Fusion）融合算法。

将密集检索和稀疏检索的两路召回结果按 RRF 分数合并去重排序。
"""


def rrf_fusion(
    dense_results: list[dict],
    sparse_results: list[dict],
    k: int = 60,
    final_top_k: int = 4,
) -> list[dict]:
    """RRF 融合两路检索结果。

    RRF_score(doc) = Σ 1 / (k + rank_i(doc))
    其中 rank_i 从 0 开始，k 为平滑常数（默认 60）。
    """
    if not dense_results and not sparse_results:
        return []

    doc_map: dict[str, dict] = {}

    for rank, item in enumerate(dense_results):
        text = item.get("text", "")
        if not text:
            continue
        if text not in doc_map:
            doc_map[text] = dict(item)
            doc_map[text]["rrf_score"] = 0.0
        doc_map[text]["rrf_score"] += 1.0 / (k + rank)

    for rank, item in enumerate(sparse_results):
        text = item.get("text", "")
        if not text:
            continue
        if text not in doc_map:
            doc_map[text] = dict(item)
            doc_map[text]["rrf_score"] = 0.0
        doc_map[text]["rrf_score"] += 1.0 / (k + rank)

    merged = sorted(doc_map.values(), key=lambda x: x["rrf_score"], reverse=True)
    return merged[:final_top_k]
