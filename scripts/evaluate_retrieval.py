"""
3.10 Evaluation baseline.
"""

import asyncio

import pandas as pd

from app.rag.retriever import retrieve

DATASET_PATH = "data/rag_dataset.xlsx"


async def run_evaluation():
    df = pd.read_excel(DATASET_PATH, sheet_name="RAG_Evaluation")
    df = df[df["ID"].notna()]

    top3_hits = 0
    top5_hits = 0
    failures = []

    for _, row in df.iterrows():
        query = row["Query"]
        expected_id = str(row["Expected Record"])

        results = await retrieve(query, top_k=5)
        retrieved_ids = [r.id for r in results]

        hit_top3 = expected_id in retrieved_ids[:3]
        hit_top5 = expected_id in retrieved_ids[:5]

        if hit_top3:
            top3_hits += 1
        if hit_top5:
            top5_hits += 1
        else:
            failures.append(
                {
                    "eval_id": row["ID"],
                    "query": query,
                    "expected": expected_id,
                    "got": [(r.id, r.similarity) for r in results],
                }
            )

    total = len(df)
    print("\n--- Retrieval Evaluation Report ---")
    print(f"Total queries: {total}")
    print(f"Top-3 accuracy: {top3_hits}/{total} ({100 * top3_hits / total:.1f}%)")
    print(f"Top-5 accuracy: {top5_hits}/{total} ({100 * top5_hits / total:.1f}%)")

    if failures:
        print(f"\nFailure cases ({len(failures)}):")
        for f in failures:
            print(f"  [{f['eval_id']}] \"{f['query']}\"")
            print(f"      expected: {f['expected']}")
            print(f"      got: {f['got']}")
    print("------------------------------------")


if __name__ == "__main__":
    asyncio.run(run_evaluation())