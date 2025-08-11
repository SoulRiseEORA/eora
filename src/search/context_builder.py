from typing import List, Dict, Any


def summarize_with_sources(snippets: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    for i, snip in enumerate(snippets, start=1):
        src = snip.get("source_id") or snip.get("id") or "unknown"
        date = snip.get("date") or snip.get("time", {}).get("observed_at") or ""
        text = snip.get("text") or snip.get("content") or ""
        if len(text) > 600:
            text = text[:600] + " …"
        lines.append(f"[{i}] ({src} {date})\n{text}\n")
    return "\n".join(lines)

