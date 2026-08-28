"""
3.10 Evaluation baseline.
"""

import asyncio

import pandas as pd

from app.rag.retriever import retrieve


DATASET_PATH = "data/rag_dataset.xlsx"


async def run_evaluation() -> None:
    """
    Evaluate RAG retrieval against the approved
    RAG_Evaluation sheet.
    """

    df = pd.read_excel(
        DATASET_PATH,
        sheet_name="RAG_Evaluation",
    )

    # Keep only valid evaluation rows.
    df = df[
        df["ID"].notna()
        & df["Query"].notna()
        & df["Expected Record"].notna()
    ]

    top3_hits = 0
    top5_hits = 0
    failures = []

    for _, row in df.iterrows():

        query = str(row["Query"]).strip()
        expected_id = str(
            row["Expected Record"]
        ).strip()

        results = await retrieve(
            query=query,
            top_k=5,
        )

        retrieved_ids = [
            str(result.id).strip()
            for result in results
        ]

        hit_top3 = (
            expected_id in retrieved_ids[:3]
        )

        hit_top5 = (
            expected_id in retrieved_ids[:5]
        )

        if hit_top3:
            top3_hits += 1

        if hit_top5:
            top5_hits += 1

        else:
            failures.append(
                {
                    "eval_id": str(
                        row["ID"]
                    ).strip(),
                    "query": query,
                    "expected": expected_id,
                    "got": [
                        (
                            result.id,
                            result.similarity,
                        )
                        for result in results
                    ],
                }
            )

    total = len(df)

    print(
        "\n--- Retrieval Evaluation Report ---"
    )

    print(
        f"Total queries: {total}"
    )

    if total == 0:
        print(
            "No valid evaluation queries found."
        )
        print(
            "------------------------------------"
        )
        return

    top3_accuracy = (
        100 * top3_hits / total
    )

    top5_accuracy = (
        100 * top5_hits / total
    )

    print(
        f"Top-3 accuracy: "
        f"{top3_hits}/{total} "
        f"({top3_accuracy:.1f}%)"
    )

    print(
        f"Top-5 accuracy: "
        f"{top5_hits}/{total} "
        f"({top5_accuracy:.1f}%)"
    )

    if failures:

        print(
            f"\nFailure cases "
            f"({len(failures)}):"
        )

        for failure in failures:

            print(
                f'  [{failure["eval_id"]}] '
                f'"{failure["query"]}"'
            )

            print(
                f'      expected: '
                f'{failure["expected"]}'
            )

            print(
                f'      got: '
                f'{failure["got"]}'
            )

    print(
        "------------------------------------"
    )


if __name__ == "__main__":
    asyncio.run(
        run_evaluation()
    )