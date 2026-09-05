"""
Day 8 RAG retrieval evaluation.

- Runs the approved RAG_Evaluation sheet.
- Separates stale evaluation rows whose expected records no longer
  exist in the current knowledge index.
- Reports Top-3 / Top-5 accuracy only for valid current records.
- Adds realistic Day 8 diagnostic queries including SaaS and
  AI-powered MVP development.
"""

import asyncio

import pandas as pd
from sqlalchemy import select

from app.db.models import KnowledgeChunk
from app.db.session import AsyncSessionLocal
from app.rag.retriever import retrieve


DATASET_PATH = "data/rag_dataset.xlsx"


EXTRA_DIAGNOSTIC_QUERIES = [
    "Do you provide SaaS development services?",
    "Can you build an AI-powered SaaS product?",
    "Can MoinSystems AI help me build an MVP?",
    "Can you develop an AI-powered MVP for a startup?",
    "Can you build an AI chatbot for customer support?",
    "How much does an AI chatbot project cost?",
    "Can I see your previous projects?",
    "What services does MoinSystems AI provide?",
]


async def get_current_record_ids() -> set[str]:
    """
    Load the IDs that actually exist in the current RAG index.
    This lets us identify stale evaluation expectations.
    """

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(KnowledgeChunk.id)
        )

        return {
            str(record_id).strip()
            for record_id in result.scalars().all()
        }


async def run_evaluation() -> None:
    """
    Evaluate current RAG retrieval against the approved
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
    ].copy()

    current_record_ids = await get_current_record_ids()

    top3_hits = 0
    top5_hits = 0

    evaluated_count = 0

    failures = []
    stale_rows = []

    for _, row in df.iterrows():

        eval_id = str(row["ID"]).strip()
        query = str(row["Query"]).strip()
        expected_id = str(
            row["Expected Record"]
        ).strip()

        # Do not count an evaluation row as a retrieval failure
        # when its expected record no longer exists in the
        # current approved knowledge index.
        if expected_id not in current_record_ids:

            stale_rows.append(
                {
                    "eval_id": eval_id,
                    "query": query,
                    "expected": expected_id,
                }
            )

            continue

        evaluated_count += 1

        results = await retrieve(
            query=query,
            top_k=5,
        )

        retrieved_ids = [
            str(result.id).strip()
            for result in results
        ]

        hit_top3 = expected_id in retrieved_ids[:3]
        hit_top5 = expected_id in retrieved_ids[:5]

        if hit_top3:
            top3_hits += 1

        if hit_top5:
            top5_hits += 1
        else:
            failures.append(
                {
                    "eval_id": eval_id,
                    "query": query,
                    "expected": expected_id,
                    "got": [
                        (
                            str(result.id),
                            round(
                                float(result.similarity),
                                4,
                            ),
                        )
                        for result in results
                    ],
                }
            )

    print(
        "\n--- Day 8 Retrieval Evaluation Report ---"
    )

    print(
        f"Evaluation rows in sheet: {len(df)}"
    )

    print(
        f"Valid current evaluation rows: "
        f"{evaluated_count}"
    )

    print(
        f"Stale/outdated evaluation rows: "
        f"{len(stale_rows)}"
    )

    if evaluated_count == 0:

        print(
            "No current evaluation rows were available."
        )

    else:

        top3_accuracy = (
            100 * top3_hits / evaluated_count
        )

        top5_accuracy = (
            100 * top5_hits / evaluated_count
        )

        print(
            f"Top-3 accuracy: "
            f"{top3_hits}/{evaluated_count} "
            f"({top3_accuracy:.1f}%)"
        )

        print(
            f"Top-5 accuracy: "
            f"{top5_hits}/{evaluated_count} "
            f"({top5_accuracy:.1f}%)"
        )

    if stale_rows:

        print(
            "\nStale evaluation expectations "
            "(not counted as retrieval failures):"
        )

        for item in stale_rows:

            print(
                f'  [{item["eval_id"]}] '
                f'"{item["query"]}"'
            )

            print(
                f'      missing expected record: '
                f'{item["expected"]}'
            )

    if failures:

        print(
            f"\nTrue retrieval failure cases "
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

    else:

        print(
            "\nNo Top-5 failures among current "
            "evaluation records."
        )

    # -------------------------------------------------
    # Day 8 additional realistic query diagnostics
    # -------------------------------------------------

    print(
        "\n--- Additional Day 8 Diagnostic Queries ---"
    )

    for query in EXTRA_DIAGNOSTIC_QUERIES:

        results = await retrieve(
            query=query,
            top_k=5,
        )

        print(
            f'\nQuery: "{query}"'
        )

        if not results:

            print(
                "  No context retrieved."
            )

            continue

        for index, result in enumerate(
            results,
            start=1,
        ):

            print(
                f"  {index}. "
                f"{result.id} "
                f"(score="
                f"{float(result.similarity):.4f})"
            )

    print(
        "\n------------------------------------------"
    )


if __name__ == "__main__":
    asyncio.run(
        run_evaluation()
    )