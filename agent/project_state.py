#!/usr/bin/env python3
"""Build a privacy-safe, durable PetTraffic project recovery snapshot."""
from __future__ import annotations
from pathlib import Path
import json, os, sys

CONTROL_FILE = Path("reports/control-center.json")
RECOMMENDATIONS_FILE = Path("reports/recommendations.json")
OUT_MD = Path("reports/project-state.md")
OUT_JSON = Path("reports/project-state.json")
HISTORY_ROOT = Path("reports/history/project-state")
PROBLEM_STATES = {"failure", "api_error", "stale", "warning", "unknown"}
WAITING_STATES = {"running", "waiting", "missing"}


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read required state input {path}: {type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"State input must be a JSON object: {path}")
    return value


def build_state(control: dict, recommendations_doc: dict, run_id: str, commit_sha: str) -> dict:
    generated_at = control.get("generated_at")
    if not isinstance(generated_at, str) or len(generated_at) < 10:
        raise ValueError("control-center generated_at is missing or invalid")
    if not run_id:
        raise ValueError("GITHUB_RUN_ID is required")
    results = control.get("results")
    if not isinstance(results, list):
        raise ValueError("control-center results must be a list")

    normalized = []
    for item in results:
        if not isinstance(item, dict):
            continue
        normalized.append({
            "name": str(item.get("name", "Unknown process"))[:120],
            "state": str(item.get("state", "unknown"))[:40],
            "detail": str(item.get("detail", ""))[:500],
            "url": item.get("url") if isinstance(item.get("url"), str) else None,
            "created_at": item.get("created_at") if isinstance(item.get("created_at"), str) else None,
        })

    problems = [item for item in normalized if item["state"] in PROBLEM_STATES]
    waiting = [item for item in normalized if item["state"] in WAITING_STATES]
    verified = [item for item in normalized if item["state"] == "success"]
    agent = next((item for item in normalized if item["name"] == "AI agentai + control-core atmintis"), None)

    recommendation_items = recommendations_doc.get("recommendations", [])
    if not isinstance(recommendation_items, list):
        recommendation_items = []
    safe_recommendations = []
    for item in recommendation_items[:10]:
        if isinstance(item, dict):
            safe_recommendations.append({
                "id": str(item.get("id", ""))[:100],
                "priority": str(item.get("priority", "info"))[:20],
                "title": str(item.get("title", ""))[:240],
                "next_action": str(item.get("next_action", ""))[:500],
            })

    if problems:
        next_action = (f"Spręsti pirmą aptiktą problemą: {problems[0]['name']} "
                       f"({problems[0]['state']}). {problems[0]['detail']}").strip()
        overall = "needs_attention"
    elif waiting:
        next_action = f"Tęsti laukiančių patikrų stebėseną: {waiting[0]['name']}."
        overall = "in_progress"
    elif safe_recommendations:
        next_action = safe_recommendations[0]["next_action"] or "Peržiūrėti prioritetines rekomendacijas."
        overall = "review_recommendations"
    else:
        next_action = "Tęsti suplanuotą stebėseną ir kitą dieną atnaujinti būseną."
        overall = "monitoring"

    return {
        "schema_version": 1,
        "project": "PetTraffic AI",
        "generated_at": generated_at,
        "run_id": str(run_id),
        "source_commit": str(commit_sha or "unknown"),
        "overall_status": overall,
        "last_verified_stage": (
            "Kasdienės automatizacijos ir Worker/D1 būklė patikrinta valdymo centro ataskaitoje."
            if verified else
            "Šiame cikle nėra sėkmingai patvirtintų procesų; ankstesnės būsenos nekeisti."
        ),
        "next_action": next_action,
        "verified_processes": verified,
        "problems": problems,
        "pending_checks": waiting,
        "ai_agent_memory_check": agent,
        "recommendations": safe_recommendations,
        "safety_boundaries": [
            "ARO Vet svetainės, kodo ir infrastruktūros nekeisti be atskiro leidimo.",
            "Svetainės turinio automatiškai nepublikuoti; būtinas vartotojo patvirtinimas.",
            "Jokių mokamų API ar paslaugų be atskiro biudžeto patvirtinimo.",
            "Nekeisti DNS, Cloudflare teisių ar produkcinės infrastruktūros be atskiro patvirtinimo.",
            "AI rekomendacijos yra patariamosios; modelio išvestys nesuteikia vykdymo teisių.",
        ],
        "privacy": "Tik agreguotos procesų būsenos ir rekomendacijų santrauka; be lankytojų lygmens duomenų, žalių paieškos užklausų ar paslapčių.",
    }


def render_markdown(state: dict) -> str:
    labels = {
        "needs_attention": "REIKIA DĖMESIO",
        "in_progress": "VYKSTA / LAUKIAMA",
        "review_recommendations": "LAUKIA REKOMENDACIJŲ PERŽIŪROS",
        "monitoring": "STEBĖSENA",
    }
    lines = [
        "# PetTraffic AI – paskutinė patikrinta projekto būsena",
        "",
        f"- Atnaujinta: {state['generated_at']}",
        f"- Būsena: **{labels.get(state['overall_status'], state['overall_status'])}**",
        f"- GitHub run: {state['run_id']}",
        f"- Šaltinio commit: {state['source_commit']}",
        "",
        "## Paskutinis patikrintas etapas", "",
        state["last_verified_stage"], "",
        "## Kitas veiksmas", "", state["next_action"], "",
        "## Patvirtinti procesai", "",
    ]
    if state["verified_processes"]:
        lines.extend(f"- {item['name']}: {item['detail']}" for item in state["verified_processes"])
    else:
        lines.append("- Šiame cikle sėkmingų procesų nepatvirtinta.")
    lines.extend(["", "## Problemos", ""])
    if state["problems"]:
        lines.extend(
            f"- **{item['name']}** ({item['state']}): {item['detail']}"
            + (f" – {item['url']}" if item.get("url") else "")
            for item in state["problems"]
        )
    else:
        lines.append("- Šiame cikle problemų nenustatyta.")
    lines.extend(["", "## Laukiančios patikros", ""])
    if state["pending_checks"]:
        lines.extend(f"- {item['name']}: {item['detail']}" for item in state["pending_checks"])
    else:
        lines.append("- Nėra.")
    lines.extend(["", "## AI agentų ir atminties patikra", ""])
    if state["ai_agent_memory_check"]:
        agent = state["ai_agent_memory_check"]
        lines.append(f"- Būsena: **{agent['state']}** – {agent['detail']}")
        if agent.get("url"):
            lines.append(f"- Patikros šaltinis: {agent['url']}")
    else:
        lines.append("- Šiame valdymo centro cikle atskiro AI atminties įrašo nėra.")
    lines.extend(["", "## Rekomendacijos", ""])
    if state["recommendations"]:
        for item in state["recommendations"]:
            lines.append(f"- **[{item['priority']}] {item['title']}** – {item['next_action']}")
    else:
        lines.append("- Šiame cikle rekomendacijų nėra.")
    lines.extend(["", "## Nekeičiamos saugumo ribos", ""])
    lines.extend(f"- {item}" for item in state["safety_boundaries"])
    lines.extend(["", f"> {state['privacy']}", ""])
    return "\n".join(lines)


def persist_state(state: dict, history_root: Path = HISTORY_ROOT) -> tuple[Path, Path, Path]:
    day = state["generated_at"][:10]
    if len(day) != 10 or day[4] != "-" or day[7] != "-":
        raise ValueError("generated_at must begin with an ISO date (YYYY-MM-DD)")
    history_file = history_root / f"{day}.json"
    daily = {"date": day, "snapshots": []}
    if history_file.exists():
        daily = json.loads(history_file.read_text(encoding="utf-8"))
        if daily.get("date") != day or not isinstance(daily.get("snapshots"), list):
            raise ValueError(f"Invalid project-state history file: {history_file}")
    if not any(str(item.get("run_id")) == state["run_id"] for item in daily["snapshots"]):
        daily["snapshots"].append(state)
    history_root.mkdir(parents=True, exist_ok=True)
    history_file.write_text(json.dumps(daily, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest_json = history_root / "latest.json"
    latest_md = history_root / "latest.md"
    latest_json.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest_md.write_text(render_markdown(state), encoding="utf-8")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(state), encoding="utf-8")
    return history_file, latest_json, latest_md


def main() -> int:
    try:
        control = load_json(CONTROL_FILE)
        recommendations = load_json(RECOMMENDATIONS_FILE)
        state = build_state(control, recommendations, os.environ.get("GITHUB_RUN_ID", ""), os.environ.get("GITHUB_SHA", ""))
        paths = persist_state(state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Could not build durable project state: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print("Updated durable project recovery state:")
    for path in paths:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
