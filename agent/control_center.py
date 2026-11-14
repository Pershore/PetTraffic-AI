#!/usr/bin/env python3
"""Read-only daily control center for PetTraffic GitHub Actions and Cloudflare Worker/D1."""
from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
import json, os

OUT = Path("reports/control-center.md")
OUT_JSON = Path("reports/control-center.json")
REPO = os.environ.get("GITHUB_REPOSITORY", "Pershore/PetTraffic-AI")
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
# GitHub Actions cron expressions use UTC. A 60-minute grace avoids alerting
# on normal scheduler delays while still detecting a missed daily/weekly cycle.
WORKFLOWS = [
    ("daily-suite.yml", "GA4, temų radaras ir svetainės stebėjimas", 36, {"frequency": "daily", "hour": 5, "minute": 37, "grace_minutes": 60}),
    ("sync-control-api.yml", "Centrinės API sinchronizavimas", 36, None),
    ("lighthouse-audit.yml", "Lighthouse auditas", 9 * 24, {"frequency": "weekly", "weekday": 0, "hour": 7, "minute": 27, "grace_minutes": 60}),
    ("control-center.yml", "Centrinis valdymo centras", 36, {"frequency": "daily", "hour": 8, "minute": 40, "grace_minutes": 60}),
]

def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)

def current_schedule_is_due(now: datetime, schedule: dict) -> bool:
    """Return whether today's scheduled cycle has passed its grace window."""
    current = now.astimezone(timezone.utc)
    due = current.replace(
        hour=int(schedule["hour"]),
        minute=int(schedule["minute"]),
        second=0,
        microsecond=0,
    )
    grace = timedelta(minutes=int(schedule.get("grace_minutes", 60)))
    frequency = schedule.get("frequency")
    if frequency == "daily":
        return current >= due + grace
    if frequency == "weekly":
        weekday = int(schedule["weekday"])
        days_back = (current.weekday() - weekday) % 7
        due = (current - timedelta(days=days_back)).replace(
            hour=int(schedule["hour"]),
            minute=int(schedule["minute"]),
            second=0,
            microsecond=0,
        )
        return current >= due + grace
    raise ValueError(f"Unsupported schedule frequency: {frequency}")


def latest_schedule_due(now: datetime, schedule: dict) -> datetime:
    """Return the latest expected schedule time whose grace window has passed."""
    current = now.astimezone(timezone.utc)
    due = current.replace(
        hour=int(schedule["hour"]),
        minute=int(schedule["minute"]),
        second=0,
        microsecond=0,
    )
    grace = timedelta(minutes=int(schedule.get("grace_minutes", 60)))
    frequency = schedule.get("frequency")
    if frequency == "daily":
        if current < due + grace:
            due -= timedelta(days=1)
        return due
    if frequency == "weekly":
        weekday = int(schedule["weekday"])
        days_back = (current.weekday() - weekday) % 7
        due = (current - timedelta(days=days_back)).replace(
            hour=int(schedule["hour"]),
            minute=int(schedule["minute"]),
            second=0,
            microsecond=0,
        )
        if current < due + grace:
            due -= timedelta(days=7)
        return due
    raise ValueError(f"Unsupported schedule frequency: {frequency}")


def is_scheduled_run(item: dict) -> bool:
    """Accept a direct cron run or the suite explicitly marked as cron-triggered."""
    if item.get("event") == "schedule":
        return True
    title = str(item.get("display_title", ""))
    return (
        item.get("event") == "workflow_run"
        and title.startswith("Scheduled daily suite from site-check #")
    )


def evaluate_workflow(
    name: str,
    runs: list[dict],
    now: datetime,
    max_age_hours: int,
    schedule: dict | None = None,
    workflow_updated_at: str | None = None,
    workflow_state: str = "active",
) -> dict:
    if workflow_state != "active":
        return {
            "name": name,
            "state": "warning",
            "detail": f"GitHub Actions workflow neaktyvus (state: {workflow_state}).",
            "url": None,
            "created_at": None,
        }
    if not runs:
        if schedule and current_schedule_is_due(now, schedule):
            due = now.astimezone(timezone.utc).replace(
                hour=int(schedule["hour"]),
                minute=int(schedule["minute"]),
                second=0,
                microsecond=0,
            )
            if workflow_updated_at:
                try:
                    workflow_updated = parse_time(workflow_updated_at)
                except (TypeError, ValueError):
                    return {
                        "name": name,
                        "state": "unknown",
                        "detail": "GitHub Actions workflow atnaujinimo data neatpažinta.",
                        "url": None,
                        "created_at": None,
                    }
                if workflow_updated > due:
                    return {
                        "name": name,
                        "state": "waiting",
                        "detail": (
                            f"Workflow atnaujintas {workflow_updated.strftime('%Y-%m-%d %H:%M')} UTC "
                            "po paskutinio suplanuoto laiko; laukiama kito ciklo."
                        ),
                        "url": None,
                        "created_at": None,
                    }
            return {
                "name": name,
                "state": "warning",
                "detail": f"Suplanuotas ciklas ({due.strftime('%H:%M')} UTC) praėjo su atsargos laiku, tačiau paleidimo nerasta.",
                "url": None,
                "created_at": None,
            }
        return {"name": name, "state": "missing", "detail": "Dar nėra pirmo užregistruoto paleidimo; laukiama artimiausio suplanuoto ciklo.", "url": None, "created_at": None}
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
        # A push/manual run must not hide the state of the daily schedule.
        if not schedule or is_scheduled_run(latest):
            return {**base, "state": "running", "detail": f"Vyksta ({status})."}
    if status != "completed":
        return {**base, "state": "unknown", "detail": f"Nežinoma būsena: {status}."}
    if conclusion == "failure":
        return {**base, "state": "failure", "detail": "Paskutinis paleidimas nepavyko."}
    if conclusion in ("cancelled", "timed_out", "action_required", "startup_failure"):
        # GitHub may cancel a queued non-scheduled run when another run enters
        # the same concurrency group. Judge the cron run below instead.
        if not (schedule and conclusion == "cancelled" and not is_scheduled_run(latest)):
            return {**base, "state": "warning", "detail": f"Paskutinio paleidimo rezultatas: {conclusion}."}
    if conclusion not in ("success", "neutral", "skipped"):
        return {**base, "state": "unknown", "detail": f"Nežinoma išvada: {conclusion}."}
    if schedule:
        due = latest_schedule_due(now, schedule)
        scheduled_runs = [item for item in runs if is_scheduled_run(item)]
        scheduled_latest = max(
            scheduled_runs,
            key=lambda item: item.get("created_at", ""),
            default=None,
        )
        scheduled_created_raw = scheduled_latest.get("created_at", "") if scheduled_latest else ""
        try:
            scheduled_created = parse_time(scheduled_created_raw) if scheduled_latest else None
        except (TypeError, ValueError):
            return {
                **base,
                "state": "unknown",
                "detail": "Suplanuoto paleidimo data neatpažinta.",
            }
        if workflow_updated_at:
            try:
                workflow_updated = parse_time(workflow_updated_at)
            except (TypeError, ValueError):
                return {
                    **base,
                    "state": "unknown",
                    "detail": "GitHub Actions workflow atnaujinimo data neatpažinta.",
                }
            # A current schedule-backed run after the latest workflow edit is valid,
            # even when the edit itself happened after the nominal cron time.
            if workflow_updated > due and (
                scheduled_created is None or scheduled_created < workflow_updated
            ):
                return {
                    **base,
                    "state": "waiting",
                    "detail": (
                        f"Workflow atnaujintas {workflow_updated.strftime('%Y-%m-%d %H:%M')} UTC "
                        "po paskutinio suplanuoto laiko; laukiama kito ciklo."
                    ),
                }
        if scheduled_created is None or scheduled_created < due:
            scheduled_detail = (
                f"paskutinis suplanuotas paleidimas buvo {scheduled_created_raw}"
                if scheduled_created_raw else "suplanuotų paleidimų istorijoje nėra"
            )
            return {
                **base,
                "state": "warning",
                "detail": (
                    f"Suplanuotas ciklas nuo {due.strftime('%Y-%m-%d %H:%M')} UTC dar neįvykdytas; "
                    f"{scheduled_detail}. Kiti paleidimo tipai (push / PR / rankinis) jo nepakeičia."
                ),
            }
        scheduled_status = scheduled_latest.get("status")
        scheduled_conclusion = scheduled_latest.get("conclusion")
        if scheduled_status in ("queued", "in_progress", "waiting", "pending"):
            return {
                **base,
                "state": "running",
                "detail": f"Suplanuotas ciklas vykdomas ({scheduled_status}).",
            }
        if scheduled_conclusion == "failure":
            return {
                **base,
                "state": "failure",
                "detail": "Paskutinis suplanuotas ciklas nepavyko.",
            }
        if scheduled_conclusion not in ("success", "neutral", "skipped"):
            return {
                **base,
                "state": "warning",
                "detail": f"Suplanuoto ciklo išvada nepatvirtinta: {scheduled_conclusion}.",
            }
    if age > timedelta(hours=max_age_hours):
        hours = int(age.total_seconds() // 3600)
        return {**base, "state": "stale", "detail": f"Paskutinis sėkmingas paleidimas prieš {hours} val.; tikėtasi per {max_age_hours} val."}
    return {**base, "state": "success", "detail": "Paskutinis paleidimas sėkmingas."}

def fetch_runs(workflow_file: str) -> list[dict]:
    endpoint = f"https://api.github.com/repos/{REPO}/actions/workflows/{quote(workflow_file, safe='')}/runs?branch=main&per_page=100"
    request = Request(endpoint, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PetTraffic-ControlCenter/1.0",
    })
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8")).get("workflow_runs", [])

def fetch_workflow_metadata(workflow_file: str) -> dict:
    """Read activation state and the actual last commit touching the workflow file."""
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PetTraffic-ControlCenter/1.0",
    }
    endpoint = (
        f"https://api.github.com/repos/{REPO}/actions/workflows/"
        f"{quote(workflow_file, safe='')}"
    )
    request = Request(endpoint, headers=headers)
    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("GitHub workflow metadata response is not an object")

    # The workflow resource's updated_at can lag behind changes to the YAML file.
    # Use the latest commit touching the actual workflow file as the schedule baseline.
    workflow_path = quote(f".github/workflows/{workflow_file}", safe="")
    commits_endpoint = (
        f"https://api.github.com/repos/{REPO}/commits"
        f"?path={workflow_path}&per_page=1"
    )
    commits_request = Request(commits_endpoint, headers=headers)
    with urlopen(commits_request, timeout=15) as response:
        commits = json.loads(response.read().decode("utf-8"))
    if not isinstance(commits, list) or not commits:
        raise ValueError("GitHub did not return commit history for workflow file")
    commit = commits[0].get("commit", {})
    commit_dates = commit.get("committer", {}) or {}
    author_dates = commit.get("author", {}) or {}
    last_file_commit = commit_dates.get("date") or author_dates.get("date")
    if not last_file_commit:
        raise ValueError("GitHub workflow file commit has no timestamp")
    return {
        "state": payload.get("state", "unknown"),
        "updated_at": last_file_commit,
    }


def evaluate_agent_orchestration(
    payload: dict,
    url: str | None = None,
    now: datetime | None = None,
) -> dict:
    """Check the daily AI agent run and durable control-core memory after 10:40 Vilnius time."""
    base = {"name": "AI agentai + control-core atmintis", "url": url, "created_at": None}
    agent = payload.get("agent_orchestration") if isinstance(payload, dict) else None
    if not isinstance(agent, dict):
        agent = {"status": "not_started"}

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    local_now = current.astimezone(ZoneInfo("Europe/Vilnius"))
    before_daily_check = (local_now.hour * 60 + local_now.minute) < (10 * 60 + 40)
    today = local_now.date().isoformat()
    status = agent.get("status", "unknown")
    run_date = agent.get("run_date")

    if run_date is not None:
        try:
            date.fromisoformat(str(run_date))
        except ValueError:
            return {**base, "state": "failure", "detail": "AI agent returned an invalid run_date."}

    if status == "failed":
        if run_date != today and before_daily_check:
            return {**base, "state": "waiting", "detail": "Ankstesnis AI agentų ciklas nepavyko; laukiama šiandienos 10:20 Lietuvos laiku ciklo."}
        code = agent.get("error_code") or "unknown_error"
        calls = agent.get("ai_calls", "unknown")
        return {**base, "state": "failure", "detail": f"AI agentų ciklas nepavyko ({run_date or 'unknown date'}); AI kvietimų: {calls}; klaida: {code}."}

    if status in ("not_started", "unknown"):
        if before_daily_check:
            return {**base, "state": "waiting", "detail": "AI agentų dienos ciklas dar neatėjo; tikrinimas numatytas po 10:20 Lietuvos laiku."}
        return {**base, "state": "warning", "detail": "Po suplanuoto 10:20 Lietuvos laiku ciklo nėra AI agentų vykdymo įrašo."}

    if status in ("running", "in_progress"):
        started_at = agent.get("started_at")
        if isinstance(started_at, str):
            try:
                started = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)
                age = current.astimezone(timezone.utc) - started.astimezone(timezone.utc)
                if age <= timedelta(minutes=20):
                    return {**base, "state": "running", "detail": f"AI agentų ciklas dar vykdomas ({agent.get('ai_calls', 'unknown')} AI kvietimai)."}
            except ValueError:
                pass
        return {**base, "state": "warning", "detail": "AI agentų ciklas per ilgai vykdomas arba jo pradžios laikas netinkamas."}

    if status != "completed":
        return {**base, "state": "warning", "detail": f"Neatpažinta AI agentų ciklo būsena: {status}."}

    if run_date != today:
        if before_daily_check:
            return {**base, "state": "waiting", "detail": "Paskutinis AI agentų ciklas yra iš ankstesnės dienos; laukiama šiandienos suplanuoto ciklo."}
        return {**base, "state": "stale", "detail": f"Po 10:20 Lietuvos laiku nėra šiandienos AI agentų ciklo; paskutinis įrašas: {run_date or 'unknown'}."}

    core = payload.get("control_core") if isinstance(payload, dict) else None
    if not isinstance(core, dict):
        return {**base, "state": "warning", "detail": "AI agentai baigė darbą, tačiau control-core sprendimo būsena nepateikta."}
    memory_status = core.get("memory_status")
    core_status = core.get("status")
    recommendations = core.get("recommendation_count", 0)
    gaps = core.get("evidence_gap_count", 0)
    if memory_status != "present":
        return {**base, "state": "warning", "detail": "AI agentų ciklas baigėsi, tačiau ilgalaikė control-core atmintis neišsaugota."}
    if core_status == "needs_evidence" or int(gaps or 0) > 0:
        return {**base, "state": "warning", "detail": f"AI agentų ciklas ir atminties įrašymas baigti; rekomendacijų: {recommendations}; trūksta įrodymų: {gaps}."}
    if core_status == "reviewed":
        return {**base, "state": "success", "detail": f"AI agentų ciklas baigtas; control-core atmintis išsaugota; rekomendacijų: {recommendations}; įrodymų spragų nėra."}
    return {**base, "state": "warning", "detail": f"Control-core būsena nepatvirtinta: {core_status or 'unknown'}."}


def evaluate_worker_health(
    payload: dict,
    status_code: int = 200,
    url: str | None = None,
    now: datetime | None = None,
) -> dict:
    """Evaluate Worker/D1 connectivity and the latest 15-minute site heartbeat."""
    base = {"name": "Cloudflare Worker + D1", "url": url, "created_at": None}
    if status_code != 200:
        return {**base, "state": "failure", "detail": f"Worker health endpoint returned HTTP {status_code}."}
    if not isinstance(payload, dict):
        return {**base, "state": "failure", "detail": "Worker health endpoint returned an invalid JSON structure."}
    if payload.get("ok") is not True or payload.get("database") != "connected":
        return {**base, "state": "failure", "detail": "Worker or D1 health check did not confirm a connected database."}

    heartbeat = payload.get("heartbeat")
    if heartbeat is None:
        return {**base, "state": "warning", "detail": "Worker ir D1 pasiekiami, tačiau dar nėra išsaugoto periodinio heartbeat įrašo."}
    if not isinstance(heartbeat, dict) or not isinstance(heartbeat.get("checked_at"), str):
        return {**base, "state": "failure", "detail": "Worker returned an invalid scheduled-heartbeat record."}
    try:
        checked_at = datetime.fromisoformat(heartbeat["checked_at"].replace("Z", "+00:00"))
        if checked_at.tzinfo is None:
            checked_at = checked_at.replace(tzinfo=timezone.utc)
    except ValueError:
        return {**base, "state": "failure", "detail": "Worker returned an invalid heartbeat timestamp."}

    current = now or datetime.now(timezone.utc)
    age = current - checked_at.astimezone(timezone.utc)
    if age < timedelta(minutes=-5):
        return {**base, "state": "failure", "detail": "Worker heartbeat timestamp is unexpectedly in the future."}
    if age > timedelta(minutes=45):
        minutes = int(age.total_seconds() // 60)
        return {**base, "state": "failure", "detail": f"Worker heartbeat is stale ({minutes} min); expected a check every 15 min."}
    if heartbeat.get("site_ok") is not True:
        return {**base, "state": "failure", "detail": f"Scheduled site check failed (HTTP {heartbeat.get('site_status', 'unknown')})."}
    if heartbeat.get("database_ok") is not True:
        return {**base, "state": "failure", "detail": "Scheduled heartbeat could not confirm D1 database connectivity."}

    minutes = max(0, int(age.total_seconds() // 60))
    return {**base, "state": "success", "detail": f"Worker API ir D1 veikia; svetainės heartbeat sėkmingas prieš {minutes} min."}


def fetch_worker_health() -> list[dict]:
    api_url = os.environ.get(
        "PETTRAFFIC_CONTROL_API_URL",
        "https://pettraffic-control-api.pauliusgrubliauskis.workers.dev",
    ).rstrip("/")
    health_url = api_url + "/health"
    request = Request(health_url, headers={"Accept": "application/json", "User-Agent": "PetTraffic-ControlCenter/1.0"})
    try:
        with urlopen(request, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return [
                evaluate_worker_health(payload, response.status, health_url),
                evaluate_agent_orchestration(payload, health_url),
            ]
    except HTTPError as exc:
        return [evaluate_worker_health({}, exc.code, health_url)]
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        return [{
            "name": "Cloudflare Worker + D1",
            "state": "api_error",
            "detail": f"Worker health patikra nepavyko ({type(exc).__name__}).",
            "url": health_url,
            "created_at": None,
        }]


def needs_attention(results: list[dict]) -> bool:
    """Only actionable failures and stale/uncertain checks create an alert."""
    return any(item["state"] in ("failure", "api_error", "stale", "warning", "unknown") for item in results)


def recovery_confirmed(results: list[dict]) -> bool:
    """An existing alert may be closed only when every monitored check is healthy."""
    return bool(results) and all(item.get("state") == "success" for item in results)

def render(results: list[dict], generated: datetime) -> str:
    labels = {"success":"GERAI","failure":"KLAIDA","warning":"ĮSPĖJIMAS","stale":"PASENĘ","missing":"LAUKIAMA PIRMŲ CIKLŲ","waiting":"LAUKIAMA KITO CIKLO","running":"VYKDOMA","unknown":"NEAIŠKU","api_error":"API KLAIDA"}
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
    warnings = [x for x in results if x["state"] in ("warning", "stale", "unknown")]
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
    for filename, label, max_age, schedule in WORKFLOWS:
        try:
            metadata = fetch_workflow_metadata(filename)
            item = evaluate_workflow(
                label,
                fetch_runs(filename),
                now,
                max_age,
                schedule,
                workflow_updated_at=metadata.get("updated_at"),
                workflow_state=metadata.get("state", "unknown"),
            )
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            item = {"name":label,"state":"api_error","detail":f"GitHub API patikra nepavyko ({type(exc).__name__}).","url":None,"created_at":None}
        results.append(item)
    results.extend(fetch_worker_health())
    report = render(results, now)
    OUT.write_text(report, encoding="utf-8")
    OUT_JSON.write_text(json.dumps({"generated_at": now.isoformat(), "needs_attention": needs_attention(results), "recovery_confirmed": recovery_confirmed(results), "results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report)
    # Monitored workflow incidents are report data handled by the GitHub issue alert.
    # The control-center job itself succeeded if it fetched, evaluated and wrote the report.
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
