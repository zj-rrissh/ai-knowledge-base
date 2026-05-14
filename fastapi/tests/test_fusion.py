"""测试 RRF 融合算法模块。"""

from services.fusion import rrf_fusion


class TestRrfFusion:
    def test_both_empty(self):
        assert rrf_fusion([], []) == []

    def test_dense_only(self):
        dense = [
            {"text": "chunk A", "metadata": {"source": "a.txt"}, "distance": 0.1},
            {"text": "chunk B", "metadata": {"source": "b.txt"}, "distance": 0.2},
        ]
        result = rrf_fusion(dense, [], k=60, final_top_k=3)
        assert len(result) == 2
        assert result[0]["text"] == "chunk A"

    def test_sparse_only(self):
        sparse = [
            {"text": "chunk X", "metadata": {"source": "x.txt"}, "score": 2.5},
        ]
        result = rrf_fusion([], sparse, k=60, final_top_k=3)
        assert len(result) == 1

    def test_merges_and_dedupes(self):
        dense = [
            {"text": "shared chunk", "distance": 0.1},
            {"text": "dense only", "distance": 0.3},
        ]
        sparse = [
            {"text": "shared chunk", "score": 5.0},
            {"text": "sparse only", "score": 2.0},
        ]
        result = rrf_fusion(dense, sparse, k=60, final_top_k=5)
        assert len(result) == 3
        texts = {r["text"] for r in result}
        assert texts == {"shared chunk", "dense only", "sparse only"}

    def test_rrf_boosts_dual_hit(self):
        dense = [
            {"text": "dual hit", "distance": 0.1},
            {"text": "dense hit", "distance": 0.2},
        ]
        sparse = [
            {"text": "dual hit", "score": 5.0},
        ]
        result = rrf_fusion(dense, sparse, k=60, final_top_k=5)
        assert result[0]["text"] == "dual hit"
        assert "rrf_score" in result[0]

    def test_k_parameter_affects_scores(self):
        dense = [{"text": "chunk", "distance": 0.1}]
        sparse = [{"text": "chunk", "score": 5.0}]
        r_small = rrf_fusion(dense, sparse, k=1, final_top_k=5)
        r_large = rrf_fusion(dense, sparse, k=100, final_top_k=5)
        assert r_small[0]["rrf_score"] != r_large[0]["rrf_score"]

    def test_final_top_k_limits(self):
        dense = [{"text": f"chunk {i}", "distance": 0.1} for i in range(1, 11)]
        result = rrf_fusion(dense, [], k=60, final_top_k=3)
        assert len(result) == 3

    def test_empty_text_skipped(self):
        dense = [{"text": "", "distance": 0.1}, {"text": "valid", "distance": 0.2}]
        result = rrf_fusion(dense, [], k=60, final_top_k=5)
        assert len(result) == 1
