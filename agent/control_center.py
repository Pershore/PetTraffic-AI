#!/usr/bin/env python3
"""Read-only daily control center for PetTraffic GitHub Actions and Cloudflare Worker/D1."""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import json, os

OUT = Path("reports/control-center.md")
OUT_JSON = Path("reports/control-center.json")
REPO = os.environ.get("GITHUB_REPOSITORY", "Pershore/PetTraffic-AI")
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
WORKFLOWS = [
    ("analytics-snapshot.yml", "GA4 ir Search Console", 36),
    ("sync-control-api.yml", "Centrinės API sinchronizavimas", 36),
    ("daily-topic-radar.yml", "Temų radaras", 36),
    ("live-site-monitor.yml", "Svetainės stebėjimas", 36),
    ("lighthouse-audit.yml", "Lighthouse auditas", 9 * 24),
    ("control-center.yml", "Centrinis valdymo centras", 36),
]

def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)

def evaluate_workflow(name: str, runs: list[dict], now: datetime, max_age_hours: int) -> dict:
    if not runs:
        return {"name": name, "state": "missing", "detail": "Nerasta nė vieno paleidimo.", "url": None, "created_at": None}
    latest = max(runs, key=lambda item: item.get("created_at", ""))
    created_raw = latest.get("created_at", "")
    try:
        created = parse_time(created_raw)
    except (TypeError, ValueError):
        return {"name": name, "state": "unknown", "detail": "Naujausio paleidimo data neatpažinta.", "url": latest.get("html_url"), "created_at": created_raw}
    status, conclusion = latest.get("status"), latest.get("conclusion")
    base = {"name": name, "url": latest.get("html_url"), "created_at": created_raw}
    age = now.astimezone(timezone.utc) - created
    if status in ("queued", "in_progress", "waiting", "pending"):
        return {**base, "state": "running", "detail": f"Vyksta ({status})."}
    if status != "completed":
        return {**base, "state": "unknown", "detail": f"Nežinoma būsena: {status}."}
    if conclusion == "failure":
        return {**base, "state": "failure", "detail": "Paskutinis paleidimas nepavyko."}
    if conclusion in ("cancelled", "timed_out", "action_required", "startup_failure"):
        return {**base, "state": "warning", "detail": f"Paskutinio paleidimo rezultatas: {conclusion}."}
    if conclusion not in ("success", "neutral", "skipped"):
        return {**base, "state": "unknown", "detail": f"Nežinoma išvada: {conclusion}."}
    if age > timedelta(hours=max_age_hours):
        hours = int(age.total_seconds() // 3600)
        return {**base, "state": "stale", "detail": f"Paskutinis sėkmingas paleidimas prieš {hours} val.; tikėtasi per {max_age_hours} val."}
    return {**base, "state": "success", "detail": "Paskutinis paleidimas sėkmingas."}

def fetch_runs(workflow_file: str) -> list[dict]:
    endpoint = f"https://api.github.com/repos/{REPO}/actions/workflows/{quote(workflow_file, safe='')}/runs?branch=main&per_page=5"
    request = Request(endpoint, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PetTraffic-ControlCenter/1.0",
    })
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8")).get("workflow_runs", [])

def evaluate_worker_health(payload: dict, status_code: int = 200, url: str | None = None) -> dict:
    """Evaluate the dedicated control Worker and its D1 health response."""
    base = {"name": "Cloudflare Worker + D1", "url": url, "created_at": None}
    if status_code != 200:
        return {**base, "state": "failure", "detail": f"Worker health endpoint returned HTTP {status_code}."}
    if payload.get("ok") is not True or payload.get("database") != "connected":
        return {**base, "state": "failure", "detail": "Worker or D1 health check did not confirm a connected database."}
    return {**base, "state": "success", "detail": "Worker API pasiekiamas, D1 duomenų bazė prijungta."}


def fetch_worker_health() -> dict:
    api_url = os.environ.get(
        "PETTRAFFIC_CONTROL_API_URL",
        "https://pettraffic-control-api.pauliusgrubliauskis.workers.dev",
    ).rstrip("/")
    health_url = api_url + "/health"
    request = Request(health_url, headers={"Accept": "application/json", "User-Agent": "PetTraffic-ControlCenter/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return evaluate_worker_health(payload, response.status, health_url)
    except HTTPError as exc:
        return evaluate_worker_health({}, exc.code, health_url)
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return {
            "name": "Cloudflare Worker + D1",
            "state": "api_error",
            "detail": f"Worker health patikra nepavyko ({type(exc).__name__}).",
            "url": health_url,
            "created_at": None,
        }


def needs_attention(results: list[dict]) -> bool:
    """Only actionable failures and stale/uncertain checks create an alert."""
    return any(item["state"] in ("failure", "api_error", "stale", "warning", "unknown") for item in results)

def render(results: list[dict], generated: datetime) -> str:
    labels = {"success":"GERAI","failure":"KLAIDA","warning":"ĮSPĖJIMAS","stale":"PASENĘ","missing":"NĖRA PALEIDIMŲ","running":"VYKDOMA","unknown":"NEAIŠKU","api_error":"API KLAIDA"}
    lines = [
        "# Pet traffic – centrinis valdymo skydelis", "",
        f"Atnaujinta: {generated.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "", "> Tik skaitymo režimo GitHub Actions ir Cloudflare Worker/D1 būklės suvestinė. Ji nekeičia svetainės, kodų, nustatymų ar paslapčių.",
        "", "## Automatizacijų būklė", "",
        "| Modulis | Būsena | Pastaba |", "|---|---|---|",
    ]
    for item in results:
        note = item["detail"]
        if item.get("url"):
            note += f" [Paleidimas]({item['url']})"
        lines.append(f"| {item['name']} | **{labels.get(item['state'], item['state'].upper())}** | {note} |")
    failures = [x for x in results if x["state"] in ("failure", "api_error")]
    warnings = [x for x in results if x["state"] in ("warning", "stale", "missing", "unknown")]
    running = [x for x in results if x["state"] == "running"]
    lines += ["", "## Prioritetai", ""]
    if failures: lines.append("1. **Skubu:** patikrinti nepavykusius modulius: " + ", ".join(x["name"] for x in failures) + ".")
    if warnings: lines.append(("2. " if failures else "1. ") + "**Patikrinti:** " + ", ".join(x["name"] for x in warnings) + ".")
    if running: lines.append("**Vykdoma:** " + ", ".join(x["name"] for x in running) + ".")
    if not failures and not warnings and not running: lines.append("Nerasta veiksmų reikalaujančių būsenų.")
    lines += [
        "", "## Saugumo ribos", "",
        "- GitHub Actions gali skaityti darbo eigų ir Worker/D1 sveikatos būsenas bei kurti / uždaryti vieną techninį įspėjimo issue; svetainės failų keitimo teisės nesuteiktos.",
        "- Neskaitomi ir nerodomi slapti raktai ar lankytojų asmens duomenys.",
        "- Modulis pats netaiso ir nepublikuoja pakeitimų.",
        "- IndexNow ir PR testai yra įvykiais paleidžiami procesai, todėl nevertinami kaip kasdieniai darbai.", "",
    ]
    return "\n".join(lines)

def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if not TOKEN:
        OUT.write_text("# Pet traffic – centrinis valdymo skydelis\n\nKlaida: trūksta GITHUB_TOKEN.\n", encoding="utf-8")
        print("GITHUB_TOKEN is missing.")
        return 2
    now = datetime.now(timezone.utc)
    results = []
    for filename, label, max_age in WORKFLOWS:
        try:
            item = evaluate_workflow(label, fetch_runs(filename), now, max_age)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            item = {"name":label,"state":"api_error","detail":f"GitHub API patikra nepavyko ({type(exc).__name__}).","url":None,"created_at":None}
        results.append(item)
    results.append(fetch_worker_health())
    report = render(results, now)
    OUT.write_text(report, encoding="utf-8")
    OUT_JSON.write_text(json.dumps({"generated_at": now.isoformat(), "needs_attention": needs_attention(results), "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report)
    # Monitored workflow incidents are report data handled by the GitHub issue alert.
    # The control-center job itself succeeded if it fetched, evaluated and wrote the report.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
