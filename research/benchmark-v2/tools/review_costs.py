"""Read-only decomposition of archived aggregates; no transcript-level causal claims."""
import argparse
from decimal import Decimal
import json
from pathlib import Path


def compare(archive: dict, population: str = "all_18_attempts_per_arm") -> dict:
    arms = archive[population]
    before, after = arms["previous"], arms["revised"]
    delta = lambda a, b: float(Decimal(str(b)) - Decimal(str(a)))
    return {
        "population": population,
        "interpretation": "Observed accounting differences, not causal effects or billing deductions",
        "previous": {"attempts": before["attempts"], "full_passes": before["raw_full_passes"]},
        "revised": {"attempts": after["attempts"], "full_passes": after["raw_full_passes"]},
        "credit_deltas": {k: delta(before["credits"][k], after["credits"][k])
                          for k in ("total", "root", "helper", "uncached_input", "cached_input", "output")},
        "actual_model_credit_deltas_including_helpers": {
            model: delta(before["credits_by_model"].get(model, 0), after["credits_by_model"].get(model, 0))
            for model in sorted(before["credits_by_model"].keys() | after["credits_by_model"].keys())},
        "cannot_determine": ["which root turns were coordination", "helper work avoided by the root",
                             "independent maintainability", "actual billed deductions"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--matched-17", action="store_true")
    args = parser.parse_args()
    try:
        data = json.loads(args.archive.read_text(encoding="utf-8"))
        population = "matched_17_excluding_baseline_grader_interference" if args.matched_17 else "all_18_attempts_per_arm"
        print(json.dumps(compare(data, population), indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
