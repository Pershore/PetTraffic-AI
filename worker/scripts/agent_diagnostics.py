#!/usr/bin/env python3
"""Read-only, privacy-filtered diagnostics for one Pet traffic Worker AI run."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import json
import os
import re
import sys
import urllib.error
import urllib.request

API = "https://api.cloudflare.com/client/v4"
DATABASE_NAME = "pettraffic-control"
SPECIALISTS = ("analytics", "topics", "technical-seo", "content-review")
EVENT_KINDS = ("analytics_snapshot", "topic_snapshot", "control_center_snapshot", "recommendation_snapshot")


def classify_gap(value: object) -> str:
    """Convert a model/evidence message to a bounded code; never return the message."""
    text = str(value or "").lower()
    rules = (
        ("model_output_incomplete_json", ("incomplete json", "unexpected end of json", "nepilnas json", "neužbaigtas json", "neuzbaigtas json", "json nepilnas")),
        ("model_output_malformed_json", ("not valid json", "invalid json", "neteisingas json", "netaisyklingas json", "negaliojantis json")),
        ("model_output_invalid_shape", ("expected json object", "did not match expected json object")),
        ("model_output_missing_fields", ("required fields", "did not contain required", "did not contain the required", "trūksta lauk", "truksta lauk", "privalomų lauk", "privalomu lauk", "nepateikti privalomi lauk")),
        ("model_output_empty", ("no text output", "empty model response")),
        ("workers_ai_unavailable", ("workers ai", "model unavailable", "inference failed")),
        ("analytics_snapshot_missing", ("analytics_snapshot", "ga4 snapshot")),
        ("topic_snapshot_missing", ("topic_snapshot", "topic radar snapshot")),
        ("control_center_snapshot_missing", ("control_center_snapshot",)),
        ("recommendation_snapshot_missing", ("recommendation_snapshot",)),
        ("search_console_data_missing", ("search console", "gsc query", "gsc rows", "paieškos konsol", "paieskos konsol", "paieškos užklaus", "paieskos uzklaus")),
        ("search_volume_not_available", ("search volume", "keyword volume", "paieškos apim", "paieskos apim", "paieškų apim", "paiesku apim", "raktinių žodžių apim", "raktiniu zodziu apim")),
        ("analytics_data_missing", ("ga4 data", "analytics data", "no analytics", "ga4 duomen", "analitikos duomen", "nėra ga4", "nera ga4")),
        ("source_unavailable", ("unavailable", "fetch failed", "http 4", "http 5", "nepasiekiam", "neprieinam", "nepavyko gauti", "nepavyko pasiekti", "užklausa nepavyko", "uzklausa nepavyko")),
        ("insufficient_evidence", ("insufficient", "not enough evidence", "no verified evidence", "missing evidence", "missing", "no data", "evidence", "source", "nepakanka", "trūksta įrodym", "truksta irodym", "nėra pakankamai", "nera pakankamai", "nepakanka duomen", "nepatvirtinta")),
    )
    for code, terms in rules:
        if any(term in text for term in terms):
            return code
    return "other"


def _object(value: object) -> dict | None:
    if isinstance(value, dict):
        return value
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _codes(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return sorted({classify_gap(item) for item in value if isinstance(item, str)})


def _safe_error(value: object) -> str | None:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(value))[:80] if value is not None else None


def build_diagnostics(run_date, agent_run, control_run, memory_row, event_rows, generated_at=None):
    """Build a safe summary. Raw model output, prompts, findings and source text are excluded."""
    report = _object(agent_run.get("report_json")) if agent_run else None
    specialists = report.get("specialists") if isinstance(report, dict) else {}
    if not isinstance(specialists, dict):
        specialists = {}

    specialist_summary = {}
    for specialist_id in SPECIALISTS:
        item = specialists.get(specialist_id)
        if not isinstance(item, dict):
            specialist_summary[specialist_id] = {
                "status": "missing", "evidence_gap_count": 0,
                "evidence_gap_codes": ["specialist_report_missing"],
            }
            continue
        gaps = item.get("evidence_gaps") if isinstance(item.get("evidence_gaps"), list) else []
        codes = _codes(gaps)
        if item.get("status") == "invalid_json" and not codes:
            codes = ["invalid_json_reason_not_recorded"]
        specialist_summary[specialist_id] = {
            "status": str(item.get("status") or "unknown")[:40],
            "evidence_gap_count": len(gaps),
            "evidence_gap_codes": codes,
        }

    coordinator = report.get("coordinator") if isinstance(report, dict) else {}
    if not isinstance(coordinator, dict):
        coordinator = {}
    coordinator_gaps = coordinator.get("evidence_gaps")
    coordinator_gaps = coordinator_gaps if isinstance(coordinator_gaps, list) else []

    decision = _object(control_run.get("decision_json")) if control_run else None
    decision_gaps = decision.get("evidence_gaps") if isinstance(decision, dict) else []
    decision_gaps = decision_gaps if isinstance(decision_gaps, list) else []
    memory = _object(memory_row.get("value_json")) if memory_row else None
    memory_gaps = memory.get("evidence_gaps") if isinstance(memory, dict) else []
    memory_gaps = memory_gaps if isinstance(memory_gaps, list) else []

    source_events = {}
    for kind in EVENT_KINDS:
        matches = [
            row for row in event_rows
            if row.get("kind") == kind and _is_on_vilnius_date(row.get("created_at"), run_date)
        ]
        matches.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        latest = matches[0] if matches else None
        source_events[kind] = {
            "count_on_run_date": len(matches),
            "latest_created_at": latest.get("created_at") if latest else None,
            "latest_run_id": str(latest.get("run_id"))[:40] if latest and latest.get("run_id") else None,
        }

    data_quality = report.get("data_quality") if isinstance(report, dict) else {}
    if not isinstance(data_quality, dict):
        data_quality = {}
    return {
        "schema_version": 1,
        "run_date": run_date,
        "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
        "agent_run": {
            "present": agent_run is not None,
            "status": str(agent_run.get("status") or "missing")[:20] if agent_run else "missing",
            "ai_calls": int(agent_run.get("ai_calls") or 0) if agent_run else 0,
            "started_at": agent_run.get("started_at") if agent_run else None,
            "completed_at": agent_run.get("completed_at") if agent_run else None,
            "error_code": _safe_error(agent_run.get("error_code")) if agent_run else None,
            "report_json_status": "valid_object" if report is not None else "missing_or_invalid",
            "reported_specialist_count": len(specialists),
            "data_quality": {
                "degraded_specialist_count": int(data_quality.get("degraded_specialist_count") or 0),
                "invalid_event_payload_count": int(data_quality.get("invalid_event_payload_count") or 0),
            },
        },
        "specialists": specialist_summary,
        "coordinator": {
            "status": str(coordinator.get("status") or "missing")[:40],
            "evidence_gap_count": len(coordinator_gaps),
            "evidence_gap_codes": _codes(coordinator_gaps),
            "recommendation_count": len(coordinator.get("recommendations") or [])
            if isinstance(coordinator.get("recommendations"), list) else 0,
        },
        "control_core": {
            "present": control_run is not None,
            "status": str(control_run.get("status") or "missing")[:40] if control_run else "missing",
            "created_at": control_run.get("created_at") if control_run else None,
            "decision_json_status": "valid_object" if decision is not None else "missing_or_invalid",
            "evidence_gap_count": len(decision_gaps),
            "evidence_gap_codes": _codes(decision_gaps),
            "recommendation_count": len(decision.get("recommendations") or [])
            if isinstance(decision, dict) and isinstance(decision.get("recommendations"), list) else 0,
        },
        "memory": {
            "present": memory_row is not None and memory is not None,
            "updated_at": memory_row.get("updated_at") if memory_row else None,
            "last_run_date": memory.get("last_run_date") if memory else None,
            "last_status": memory.get("last_status") if memory else None,
            "evidence_gap_codes": _codes(memory_gaps),
        },
        "source_events": source_events,
        "privacy": "No raw model output, prompts, findings, source text, analytics rows or credentials are included.",
    }


def render_markdown(data):
    lines = [
        "# Pet traffic – Worker AI read-only diagnostics",
        "",
        f"- Run date: {data['run_date']}",
        f"- Generated: {data['generated_at']}",
        f"- Worker run: {data['agent_run']['status']}; AI calls: {data['agent_run']['ai_calls']}; error: {data['agent_run']['error_code'] or 'none'}",
        f"- Control Core: {data['control_core']['status']}; evidence gaps: {data['control_core']['evidence_gap_count']}",
        f"- Memory: {'present' if data['memory']['present'] else 'missing'}; updated: {data['memory']['updated_at'] or 'unknown'}",
        "",
        "## Specialist outcomes",
        "",
        "| Specialist | Status | Gap count | Diagnostic codes |",
        "|---|---|---:|---|",
    ]
    for key, item in data["specialists"].items():
        lines.append(f"| {key} | {item['status']} | {item['evidence_gap_count']} | {', '.join(item['evidence_gap_codes']) or 'none'} |")
    lines.extend(["", "## Source snapshots on run date", "", "| Source | Count | Latest UTC | Run ID |", "|---|---:|---|---|"])
    for kind, item in data["source_events"].items():
        lines.append(f"| {kind} | {item['count_on_run_date']} | {item['latest_created_at'] or 'none'} | {item['latest_run_id'] or 'none'} |")
    lines.extend(["", "Only bounded statuses and diagnostic codes are shown. Raw prompts, model output, source text, analytics rows and credentials are excluded.", ""])
    return "\n".join(lines)


def _is_on_vilnius_date(value: object, run_date: str) -> bool:
    """Interpret D1 timestamps in the project's Vilnius-local run_date, not UTC date text."""
    if not isinstance(value, str):
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(ZoneInfo("Europe/Vilnius")).date().isoformat() == run_date
    except (TypeError, ValueError):
        return False


def _api_json(url, token, method="GET", body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        url, data=data, method=method,
        headers={"Authorization": "Bearer " + token, "Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Cloudflare D1 diagnostics request returned HTTP {exc.code}.") from None
    except Exception:
        raise RuntimeError("Cloudflare D1 diagnostics request could not be completed.") from None
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise RuntimeError("Cloudflare did not confirm the D1 diagnostics request.")
    return payload


def _resolve_database(account, token, configured_id):
    if configured_id:
        return configured_id
    payload = _api_json(f"{API}/accounts/{account}/d1/database", token)
    matches = [x for x in payload.get("result", []) if isinstance(x, dict) and x.get("name") == DATABASE_NAME]
    if len(matches) != 1:
        raise RuntimeError("Could not uniquely identify the configured Pet traffic D1 database.")
    result = matches[0].get("uuid") or matches[0].get("id")
    if not result:
        raise RuntimeError("Cloudflare did not return the D1 database identifier.")
    return str(result)


def _assert_read_only_meta(meta):
    if not isinstance(meta, dict) or "rows_written" not in meta:
        raise RuntimeError("D1 did not return write-count metadata for the read-only query.")
    if int(meta.get("rows_written") or 0) != 0:
        raise RuntimeError("Read-only diagnostics unexpectedly reported a database write.")


def _query(account, database, token, sql, params):
    if not sql.lstrip().upper().startswith("SELECT"):
        raise RuntimeError("Diagnostics only permit SELECT statements.")
    payload = _api_json(
        f"{API}/accounts/{account}/d1/database/{database}/query",
        token, "POST", {"sql": sql, "params": params},
    )
    result = payload.get("result")
    if not isinstance(result, list) or not result or result[0].get("success") is not True:
        raise RuntimeError("Cloudflare did not confirm the read-only D1 query.")
    _assert_read_only_meta(result[0].get("meta"))
    rows = result[0].get("results") or []
    return rows if isinstance(rows, list) else []


def _load_source_events(account, database, token, run_date):
    """Read a bounded set per event kind for the exact Vilnius calendar day.

    Separate kind-scoped SELECTs prevent busy Control Center streams from
    evicting the analytics/topic evidence rows from a global LIMIT.
    """
    local_start = datetime.strptime(run_date, "%Y-%m-%d").replace(
        tzinfo=ZoneInfo("Europe/Vilnius")
    )
    local_end = local_start + timedelta(days=1)
    start_utc = local_start.astimezone(timezone.utc).isoformat()
    end_utc = local_end.astimezone(timezone.utc).isoformat()
    events = []
    for kind in EVENT_KINDS:
        rows = _query(
            account, database, token,
            "SELECT kind, created_at, json_extract(payload_json, '$.run_id') AS run_id FROM events "
            "WHERE kind = ? AND created_at >= ? AND created_at < ? "
            "ORDER BY created_at DESC LIMIT 100",
            [kind, start_utc, end_utc],
        )
        events.extend(rows)
    return events


def main():
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    database_id = os.environ.get("PETTRAFFIC_D1_DATABASE_ID", "")
    if not token or not account:
        raise RuntimeError("Required Cloudflare read-only diagnostics settings are missing.")

    requested_date = os.environ.get("PETTRAFFIC_RUN_DATE", "").strip()
    if requested_date:
        datetime.strptime(requested_date, "%Y-%m-%d")
        run_date = requested_date
    else:
        run_date = datetime.now(ZoneInfo("Europe/Vilnius")).date().isoformat()

    database = _resolve_database(account, token, database_id)
    agent = _query(account, database, token,
        "SELECT run_date, status, ai_calls, started_at, completed_at, error_code, report_json FROM agent_runs WHERE run_date = ? LIMIT 1",
        [run_date])
    core = _query(account, database, token,
        "SELECT run_date, status, core_version, decision_json, created_at FROM control_core_runs WHERE run_date = ? LIMIT 1",
        [run_date])
    memory = _query(account, database, token,
        "SELECT memory_key, value_json, updated_at FROM control_core_memory WHERE memory_key = 'latest_control_decision' LIMIT 1",
        [])
    events = _load_source_events(account, database, token, run_date)

    result = build_diagnostics(
        run_date, agent[0] if agent else None, core[0] if core else None,
        memory[0] if memory else None, events,
    )
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "worker-agent-diagnostics.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (report_dir / "worker-agent-diagnostics.md").write_text(render_markdown(result), encoding="utf-8")
    print(f"Read-only Worker AI diagnostics generated for {run_date}; rows_written=0 for all seven SELECT queries.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Worker agent diagnostics failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(1)
