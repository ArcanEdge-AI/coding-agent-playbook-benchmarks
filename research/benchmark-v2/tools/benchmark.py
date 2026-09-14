"""Offline benchmark planning and paired reporting. Never launches model inference."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

STATUSES = {"completed", "timeout", "infrastructure_invalid"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def number(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def validate(config: dict) -> None:
    require(type(config.get("schema_version")) is int and config["schema_version"] == 1, "Unsupported schema_version")
    require(isinstance(config.get("study_id"), str) and bool(config["study_id"]), "study_id required")
    require(type(config.get("seed")) is int, "seed must be an integer")
    require(type(config.get("repeats")) is int and 1 <= config["repeats"] <= 100,
            "repeats must be between 1 and 100")
    require(config.get("phase") in ("development", "confirmation"), "Invalid phase")
    require(config.get("comparison") in ("instructions", "delegation_package", "helper_route"),
            "Invalid comparison")
    conditions = config.get("conditions", [])
    tasks = config.get("tasks", [])
    require(isinstance(conditions, list) and len(conditions) == 2, "Exactly two conditions required")
    require(isinstance(tasks, list) and 1 <= len(tasks) <= 1000, "Provide 1 to 1000 tasks")
    for entries, name in ((conditions, "condition"), (tasks, "task")):
        require(all(isinstance(e, dict) and isinstance(e.get("id"), str) and e["id"] for e in entries),
                f"Every {name} needs an id")
        require(len({e["id"] for e in entries}) == len(entries), f"Duplicate {name} ids")
    for c in conditions:
        require(type(c.get("helpers")) is bool, "helpers must be boolean")
        if c["helpers"]:
            require(bool(c.get("helper_model")) and bool(c.get("helper_effort")), "Helper route required")
        else:
            require(c.get("helper_model") is None and c.get("helper_effort") is None,
                    "Disabled helpers cannot have a route")
    for t in tasks:
        require(t.get("split") in ("development", "regression", "holdout"), "Invalid task split")
        require(t.get("status") in ("specification_only", "validated"), "Invalid task status")
        if config["phase"] == "confirmation":
            require(t["split"] == "holdout" and t.get("used_for_tuning") is False,
                    "Confirmation requires untouched holdout tasks")
        else:
            require(t["split"] != "holdout", "Do not expose holdouts in development")
    left, right = conditions
    if config["comparison"] == "instructions":
        require(all(left.get(k) == right.get(k) for k in ("helpers", "helper_model", "helper_effort")),
                "Instruction comparisons must hold helper capability and route fixed")
    elif config["comparison"] == "delegation_package":
        require(left["helpers"] != right["helpers"], "Delegation package needs enabled/disabled conditions")
    else:
        require(left["helpers"] and right["helpers"], "Route comparison requires helpers in both conditions")
        require((left["helper_model"], left["helper_effort"]) !=
                (right["helper_model"], right["helper_effort"]), "Helper routes must differ")
    require(isinstance(config.get("budget"), dict), "budget required")
    require(config["budget"].get("max_scored_starts") == len(tasks) * config["repeats"] * 2,
            "max_scored_starts must equal the complete paired schedule")


def readiness_issues(config: dict) -> list[str]:
    """Report missing preparation, not proof of native controls or spending authority."""
    validate(config)
    issues = []
    for task in config["tasks"]:
        if task["status"] != "validated":
            issues.append(f"{task['id']}: task fixture and independent grader are not validated")
        for key in ("source_commit", "prompt_sha256", "grader_sha256", "environment_digest", "preflight_evidence"):
            if not task.get(key):
                issues.append(f"{task['id']}: missing {key}")
    for condition in config["conditions"]:
        if not condition.get("instructions_sha256"):
            issues.append(f"{condition['id']}: instruction snapshot hash is not frozen")
    for key in ("root_model", "root_effort", "cli_version", "author_seconds", "grader_seconds",
                "runtime_control_evidence", "prompt_parity_evidence", "accounting_evidence", "rate_card_sha256"):
        if not config.get("runtime", {}).get(key):
            issues.append(f"runtime: missing {key}")
    budget = config["budget"]
    if budget.get("approved") is not True or not budget.get("approval_reference"):
        issues.append("No explicit inference/budget authorization recorded")
    for key in ("total_credit_limit", "per_attempt_credit_reserve", "probe_credit_allowance"):
        if not number(budget.get(key)) or budget[key] <= 0:
            issues.append(f"budget: set a positive {key}")
    return issues


def schedule(config: dict) -> dict:
    """Alternate order within tasks; balance odd repeats across tasks; shuffle pairs."""
    validate(config)
    rng = random.Random(config["seed"])
    tasks = sorted(config["tasks"], key=lambda t: t["id"])
    rng.shuffle(tasks)
    arms = [c["id"] for c in config["conditions"]]
    pairs = []
    for index, task in enumerate(tasks):
        for repeat in range(1, config["repeats"] + 1):
            order = arms if (index + repeat) % 2 else arms[::-1]
            pairs.append({"task_id": task["id"], "repeat": repeat, "condition_order": order[:]})
    rng.shuffle(pairs)
    digest = hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"study_id": config["study_id"], "plan_sha256": digest,
            "preview_only": True, "launch_authorized_by_tool": False,
            "scored_starts": len(pairs) * 2, "readiness_issues": readiness_issues(config), "pairs": pairs}


def summarize(config: dict, rows: list[dict]) -> dict:
    """Require scheduled identities; retain failed spending; isolate invalid pairs."""
    require(isinstance(rows, list), "Results must be a JSON array")
    plan = schedule(config)
    arms = [c["id"] for c in config["conditions"]]
    expected = {(p["task_id"], p["repeat"], a) for p in plan["pairs"] for a in arms}
    indexed = {}
    for row in rows:
        require(isinstance(row, dict), "Every result must be an object")
        key = (row.get("task_id"), row.get("repeat"), row.get("condition"))
        require(row.get("study_id") == config["study_id"], "Wrong study_id")
        require(type(row.get("repeat")) is int and key in expected, "Unscheduled result")
        require(key not in indexed, "Duplicate result; retain retries under a separate approved study")
        require(row.get("status") in STATUSES, "Invalid result status")
        require(type(row.get("submitted")) is bool, "submitted must be boolean")
        for field in ("functional_pass", "quality_pass"):
            require(row.get(field) is None or type(row[field]) is bool, f"Invalid {field}")
        require(not row.get("functional_pass") or row["submitted"], "Passing code must have been submitted")
        if row["status"] != "infrastructure_invalid":
            require(type(row.get("functional_pass")) is bool, "Valid attempts require an external functional grade")
        for field in ("root_credits", "helper_credits"):
            require(row.get(field) is None or number(row[field]), f"Invalid {field}")
        require(type(row.get("helper_count")) is int and row["helper_count"] >= 0, "Invalid helper_count")
        condition = next(c for c in config["conditions"] if c["id"] == row["condition"])
        if not condition["helpers"] and row["helper_count"] > 0:
            require(row["status"] == "infrastructure_invalid", "Helper in disabled arm invalidates its pair")
        indexed[key] = row
    matched = []
    for pair in plan["pairs"]:
        keys = [(pair["task_id"], pair["repeat"], a) for a in arms]
        if all(k in indexed and indexed[k]["status"] != "infrastructure_invalid" for k in keys):
            matched.extend(keys)
    report = {"study_id": config["study_id"], "scoring": "descriptive_only_no_automatic_winner",
              "expected_starts": len(expected), "received_starts": len(rows),
              "missing_starts": len(expected) - len(rows), "matched_pairs": len(matched) // 2,
              "infrastructure_invalid_starts": sum(r["status"] == "infrastructure_invalid" for r in rows),
              "conditions": {}}
    for arm in arms:
        all_rows = [r for r in rows if r["condition"] == arm]
        selected = [indexed[k] for k in matched if k[2] == arm]
        pending = sum(r["functional_pass"] and r.get("quality_pass") is None for r in selected)
        accepted = sum(r["functional_pass"] and r.get("quality_pass") is True for r in selected)
        known_cost = lambda rs: sum(r.get(f) or 0 for r in rs for f in ("root_credits", "helper_credits"))
        complete_cost = lambda rs: all(r.get(f) is not None for r in rs for f in ("root_credits", "helper_credits"))
        matched_cost_complete = bool(selected) and complete_cost(selected)
        report["conditions"][arm] = {
            "matched_attempts": len(selected), "functional_passes": sum(r["functional_pass"] for r in selected),
            "known_accepted": accepted, "acceptance_pending": pending,
            "timeouts": sum(r["status"] == "timeout" for r in selected),
            "enabled_non_delegating_attempts": sum(r["helper_count"] == 0 for r in selected)
                if next(c for c in config["conditions"] if c["id"] == arm)["helpers"] else None,
            "matched_cost_complete": matched_cost_complete,
            "matched_known_credit_subtotal": known_cost(selected),
            "credits_per_accepted": known_cost(selected) / accepted
                if accepted and not pending and matched_cost_complete else None,
            "all_recorded_known_credit_subtotal": known_cost(all_rows),
            "all_recorded_cost_complete": bool(all_rows) and complete_cost(all_rows)}
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "schedule", "summarize"))
    parser.add_argument("plan", type=Path)
    parser.add_argument("--results", type=Path, help="JSON array of scored records")
    parser.add_argument("--require-prepared", action="store_true", help="Fail on missing preparation fields")
    args = parser.parse_args()
    try:
        config = json.loads(args.plan.read_text(encoding="utf-8"))
        validate(config)
        if args.command == "summarize":
            require(args.results is not None, "summarize requires --results")
            result = summarize(config, json.loads(args.results.read_text(encoding="utf-8")))
        elif args.command == "schedule":
            result = schedule(config)
        else:
            result = {"schema_valid": True, "launch_authorized_by_tool": False,
                      "readiness_issues": readiness_issues(config)}
        print(json.dumps(result, indent=2, allow_nan=False))
        return 1 if args.require_prepared and readiness_issues(config) else 0
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
