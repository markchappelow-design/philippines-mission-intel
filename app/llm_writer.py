from pathlib import Path
from openai import OpenAI

from app.models import SourceItem


def _load_prompt() -> str:
    return Path("prompts/philippines_report_prompt.txt").read_text(encoding="utf-8")


def _build_source_block(items: list[SourceItem]) -> str:
    lines = []
    for item in items:
        lines.append(
            f"""SOURCE: {item.source_name}
URL: {item.source_url}
SECTION: {item.section_target}
STATUS: {item.fetch_status}
PUBLISHED_UTC: {item.published_time_utc}
TITLE: {item.title}
TEXT:
{item.extracted_text[:5000]}
"""
        )
    return "\n\n".join(lines)


def _build_section_context_block(section_context: dict) -> str:
    lines = []
    for heading, payload in section_context.items():
        lines.append(
            f"""SECTION: {heading}
CONFIDENCE: {payload['confidence']}
SOURCE_COUNT: {payload['source_count']}"""
        )
    return "\n\n".join(lines)


def generate_report(
    openai_api_key: str,
    model: str,
    items: list[SourceItem],
    section_context: dict,
    delta_lines: list[str],
) -> str:
    client = OpenAI(api_key=openai_api_key)
    prompt = _load_prompt()
    source_block = _build_source_block(items)
    section_block = _build_section_context_block(section_context)
    delta_block = "\n".join(delta_lines)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": (
                    "Use the following source notes, section confidence context, "
                    "and prior-run delta notes to write the report.\n\n"
                    f"SECTION CONTEXT:\n{section_block}\n\n"
                    f"DELTA NOTES:\n{delta_block}\n\n"
                    f"SOURCE NOTES:\n{source_block}"
                ),
            },
        ],
    )
    return response.output_text.strip()