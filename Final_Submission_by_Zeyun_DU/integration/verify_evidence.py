#!/usr/bin/env python3
"""Check archive provenance and reproduce integration tables from recorded cases."""

import argparse
from collections import defaultdict
import csv
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
from statistics import median

from run_benchmark import ARCHIVE, BANKS, FLAGS, METHODS, REPO, sha256


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CASE_NAMES = {f"case_{number:03d}.txt" for number in range(1, 26)}
CASE_KEYS = {(bank, name) for bank in BANKS for name in CASE_NAMES}
CSV_METRICS = ("status", "area", "delay", "runtime_ms", "target_met")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def cell(value, places):
    return "" if value is None else f"{value:.{places}f}"


def grouped(rows, field):
    groups = defaultdict(list)
    for row in rows:
        groups[row[field]].append(row)
    return groups


def check_cases(rows, fields, expected, label):
    keys = [tuple(row[field] for field in fields) for row in rows]
    require(len(keys) == len(expected) and set(keys) == expected, f"Case coverage: {label}")


def check_archive():
    manifest = read_json(ARCHIVE / "PROVENANCE.json")
    expected = "59e33505616d127fc06a63580ca3ae3c34d1da72"
    require(manifest["commit"] == expected, "Wrong upstream commit")
    for row in manifest["imported_files"]:
        content = (ARCHIVE / row["path"]).read_bytes()
        require(len(content) == row["bytes"], f"Size mismatch: {row['path']}")
        digest = hashlib.sha256(content).hexdigest()
        require(digest == row["sha256"], f"SHA-256 mismatch: {row['path']}")
        if "transformation" not in row:
            blob = f"blob {len(content)}\0".encode() + content
            require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                    f"Git blob mismatch: {row['path']}")


def input_metadata():
    metadata = {}
    for bank, name in sorted(CASE_KEYS):
        path = REPO / "data" / bank / name
        lines = path.read_bytes().splitlines()
        limits = [int(value) for line in lines[7:] for value in line.split()] + [0, 0]
        metadata[(bank, name)] = (
            int(lines[6]), limits[0], limits[1], 1 << int(lines[0]),
        )
    return metadata


def normalize(raw, meta):
    target, limit, ram, assignments = meta
    status = raw["status"]
    passed = status == "PASS"
    area = int(raw["area"]) if raw["area"] else None
    delay = int(raw["delay"]) if raw["delay"] else None
    runtime = Decimal(raw["runtime_ms"]) if raw["runtime_ms"] else None
    require(runtime is None or runtime >= 0, f"Invalid runtime: {raw}")
    if passed:
        require(area is not None and area >= 0 and delay is not None and delay >= 0 and
                runtime is not None and raw["target_met"] in {"yes", "no"} and
                (raw["target_met"] == "yes") == (delay <= target), f"Invalid PASS: {raw}")
    return dict(bank=raw["bank"], case=raw["case"], status=status,
                target_met=int(passed and raw["target_met"] == "yes"), area=area, delay=delay,
                runtime_ms=runtime, target=target,
                delay_slack=target - delay if passed else None, time_limit_ms=limit,
                ram_limit_kib=ram, assignments=assignments)


def summary(family, repeat, method, bank, rows):
    passed = [row for row in rows if row["status"] == "PASS"]
    delays = [row["delay"] for row in passed]
    runtimes = [row["runtime_ms"] for row in rows if row["runtime_ms"] is not None]
    ratios = [(100 * row["runtime_ms"] / row["time_limit_ms"], row["bank"], row["case"])
              for row in rows if row["time_limit_ms"] > 0 and row["runtime_ms"] is not None]
    peak = max(ratios, default=(None, "", ""))
    return dict(
        family=family, repeat=repeat, method=method, bank=bank, count=len(rows),
        evaluator_pass=len(passed), targets_met=sum(row["target_met"] for row in rows),
        full_area=sum(row["area"] for row in passed) if len(passed) == len(rows) else None,
        pass_only_area=sum(row["area"] for row in passed),
        delay_median=cell(median(delays) if delays else None, 1),
        delay_max=max(delays, default=None),
        min_target_slack=min((row["delay_slack"] for row in passed), default=None),
        runtime_count=len(runtimes), runtime_sum_s=cell(sum(runtimes) / Decimal(1000), 6),
        runtime_median_ms=cell(median(runtimes) if runtimes else None, 4),
        max_budget_pct=cell(peak[0], 4), max_budget_bank=peak[1], max_budget_case=peak[2],
    )


def upstream_rows(metadata):
    cuts = ARCHIVE / "reports/stage2-cuts-20261124/casewise.csv"
    timing = ARCHIVE / "reports/stage2-timing-20261124/public-runs.csv"
    sums = []
    early_totals = {
        "submitted": (1205667, "39.89"), "r10": (1023713, "26.07"),
        "local": (872639, "32.90"), "merged": (869773, "33.68"),
    }
    timing_totals = {"1": 884234, "2": 876694, "3": 876694}
    for path, family, key, totals in (
        (cuts, "upstream_cuts", "method", early_totals),
        (timing, "upstream_timing", "run", timing_totals),
    ):
        groups = grouped(read_csv(path), key)
        require(set(groups) == set(totals), f"Unexpected coverage in {path}")
        for label, rows in groups.items():
            check_cases(rows, ("bank", "case"), CASE_KEYS, label)
            normal = []
            for raw in rows:
                meta = metadata[(raw["bank"], raw["case"])]
                if family == "upstream_timing":
                    require(tuple(int(raw[field]) for field in
                                  ("target", "limit_ms", "ram_kib", "assignments")) == meta,
                            f"Upstream input metadata differs: {raw}")
                    require(int(raw["slack"]) == int(raw["target"]) - int(raw["delay"]),
                            f"Upstream slack differs: {raw}")
                normal.append(normalize(raw, meta))
            repeat, method = (1, label) if family == "upstream_cuts" else (int(label), "Integrated Final")
            result = summary(family, repeat, method, "both", normal)
            require(result["evaluator_pass"] == result["targets_met"] == 50, label)
            if family == "upstream_cuts":
                area, runtime = totals[label]
                require((result["full_area"], cell(Decimal(result["runtime_sum_s"]), 2)) ==
                        (area, runtime), label)
            else:
                require(result["full_area"] == totals[label], label)
            sums.append(result)
    return sums


def check_upstream_controls():
    reports = ARCHIVE / "reports"
    cuts = read_csv(reports / "stage2-cuts-20261124/paired.csv")
    check_cases(cuts, ("bank", "case"), CASE_KEYS, "paired cuts")
    saved = [int(row["area_before"]) - int(row["area_after"]) for row in cuts]
    require(saved == [int(row["area_saved"]) for row in cuts], "Paired cut savings")
    require((sum(saved), sum(d > 0 for d in saved), min(saved)) == (3165, 17, 0),
            "Paired cuts aggregate")
    factors = read_csv(reports / "stage2-factors-20261124/paired.csv")
    public = [row for row in factors if row["bank"] in BANKS]
    check_cases(public, ("bank", "case"), CASE_KEYS, "paired public factors")
    saved = [int(row["area_before"]) - int(row["area_after"]) for row in public]
    require((sum(saved), sum(d > 0 for d in saved), min(saved)) == (5, 2, 0),
            "Paired public factors aggregate")
    rss = read_csv(reports / "stage2-timing-20261124/public-rss.csv")
    check_cases(rss, ("bank", "case"), CASE_KEYS, "upstream direct RSS")
    peak = max(rss, key=lambda row: int(row["rss_kib"]))
    require((peak["bank"], peak["case"], int(peak["rss_kib"])) ==
            ("stage1", "case_024.txt", 45976), "Upstream RSS maximum")


def matched_rows(path, metadata):
    env = read_json(path / "environment.json")
    require(env.get("finished_utc") and env["compiler_flags"] == list(FLAGS), "Incomplete run")
    require(sha256(REPO / "evaluator") == env["evaluator_sha256"], "Evaluator changed")
    require(set(env["input_sha256"]) == {f"{bank}/{name}" for bank, name in CASE_KEYS},
            "Incomplete input hashes")
    for name, digest in env["input_sha256"].items():
        require(sha256(REPO / "data" / name) == digest, f"Changed case: {name}")
    require(set(env["source_sha256"]) == set(METHODS), "Missing source provenance")
    for method, hashes in env["source_sha256"].items():
        require(METHODS[method] in hashes, f"Missing entry-point hash: {method}")
        for name, digest in hashes.items():
            require(sha256(REPO / name) == digest, f"Changed matched source: {name}")

    expected_order = [(repeat, bank, method) for repeat in (1, 2)
                      for bank in (BANKS if repeat == 1 else BANKS[::-1])
                      for method in (METHODS if repeat == 1 else reversed(METHODS))]
    require([(run["repeat"], run["bank"], run["method"]) for run in env["run_order"]] ==
            expected_order, "Unexpected run order")
    all_rows = []
    all_summaries = []
    cases_by_run = {}
    for run in env["run_order"]:
        repeat, bank, method = run["repeat"], run["bank"], run["method"]
        report = path / run["report"]
        raw = read_csv(report)
        check_cases(raw, ("case",), {(name,) for name in CASE_NAMES}, report.name)
        require(run["evaluator_exit_code"] == int(any(row["status"] != "PASS" for row in raw)),
                f"Evaluator exit status disagrees with its CSV: {report}")
        replay = {}
        if method == "Integrated Final":
            doc = read_json(path / "independent" / f"{report.stem}.json")
            require(doc["independent"] and doc["all_rows_checked"], report.name)
            check_cases(doc["cases"], ("case",), {(name,) for name in CASE_NAMES}, report.name)
            replay = {r["case"]: r for r in doc["cases"]}
        rows = []
        for entry in raw:
            require(set(entry) == {"case", *CSV_METRICS}, f"Unexpected CSV columns: {report}")
            entry["bank"] = bank
            case = entry["case"]
            row = normalize(entry, metadata[(bank, case)])
            if replay:
                checked = replay[case]
                require(checked["valid"] and row["status"] == "PASS" and all(
                    row[key] == checked[key] for key in
                    ("area", "delay", "target", "assignments", "target_met")), f"Replay: {report}/{case}")
            rows.append(dict(repeat=repeat, method=method, independent_replay=int(bool(replay)), **row))
        all_rows.extend(rows)
        cases_by_run[(repeat, bank, method)] = rows
        all_summaries.append(summary("matched", repeat, method, bank, rows))
    pairs = []
    for repeat in (1, 2):
        both = {method: sorted(cases_by_run[(repeat, "stage1", method)] +
                               cases_by_run[(repeat, "stage2", method)],
                               key=lambda row: (row["bank"], row["case"])) for method in METHODS}
        for method, rows in both.items():
            all_summaries.append(summary("matched", repeat, method, "both", rows))
            if method == "Integrated Final":
                continue
            joint = [(base, final) for base, final in zip(rows, both["Integrated Final"], strict=True)
                     if base["status"] == final["status"] == "PASS"]
            da = [final["area"] - base["area"] for base, final in joint]
            dd = [final["delay"] - base["delay"] for base, final in joint]
            ratios = [final["runtime_ms"] / base["runtime_ms"] for base, final in joint
                      if base["runtime_ms"] > 0]
            pairs.append(dict(
                repeat=repeat, candidate="Integrated Final", baseline=method,
                jointly_passing_cases=len(joint), final_minus_base_area=sum(da),
                final_area_lower=sum(d < 0 for d in da), final_area_equal=da.count(0),
                final_area_higher=sum(d > 0 for d in da), final_delay_lower=sum(d < 0 for d in dd),
                final_delay_equal=dd.count(0), final_delay_higher=sum(d > 0 for d in dd),
                runtime_ratio_count=len(ratios), median_case_runtime_ratio=cell(median(ratios), 6),
                sum_runtime_ratio_common_cases=cell(sum(b["runtime_ms"] for _, b in joint) /
                                                    sum(a["runtime_ms"] for a, _ in joint), 6),
            ))
    return all_rows, all_summaries, pairs


def direct_memory(path):
    groups = grouped(read_csv(path / "direct_memory.csv"), "method")
    require(set(groups) == set(METHODS), "Missing direct-memory method")
    sums = []
    for method, rows in groups.items():
        check_cases(rows, ("bank", "case"), CASE_KEYS, method)
        peaks = [(int(row["peak_rss_kib"]), row["bank"], row["case"])
                 for row in rows if int(row["exit_code"]) == 0]
        peak, bank, case = max(peaks)
        sums.append(dict(method=method, count=len(rows), exited_zero=len(peaks),
                         median_rss_kib=cell(median(p[0] for p in peaks), 1),
                         max_rss_kib=peak, max_rss_bank=bank, max_rss_case=case))
    return sums


def output_table(path, rows, write):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output_text(path, stream.getvalue(), write)


def output_text(path, content, write):
    if write:
        path.write_bytes(content.encode())
    else:
        require(path.read_text(encoding="utf-8") == content, f"Out-of-date table: {path}")


def report_rows(summaries):
    lines = ["% Generated by integration/verify_evidence.py --write.",
             r"\newcommand{\IntegrationRows}{%"]
    for row in summaries:
        if row["bank"] != "both":
            continue
        area = f"{row['full_area']:,}" if row["full_area"] is not None else "--"
        method = "Integrated" if row["method"] == "Integrated Final" else row["method"]
        total = cell(Decimal(row["runtime_sum_s"]), 2)
        if row["runtime_count"] < row["count"]:
            total += "$^{*}$"
        lines.append(
            f"{row['repeat']} & {method} & {row['evaluator_pass']}/{row['targets_met']} & "
            f"{area} & {total} " + r"\\%"
        )
    return "\n".join(lines + ["}"]) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Regenerate derived CSVs")
    args = parser.parse_args()
    check_archive()
    metadata = input_metadata()
    historical = upstream_rows(metadata)
    check_upstream_controls()
    path = DATA / "matched"
    rows, summaries, paired = matched_rows(path, metadata)
    output_table(DATA / "matched_case_metrics.csv", rows, args.write)
    output_table(DATA / "public_summary.csv", [*historical, *summaries], args.write)
    output_table(DATA / "matched_pairs.csv", paired, args.write)
    output_table(DATA / "direct_memory_summary.csv", direct_memory(path), args.write)
    output_text(DATA / "matched_report_rows.tex", report_rows(summaries), args.write)
    print(f"Verified source hashes, {len(rows)} matched evaluator observations, "
          "100 independent final replays, 200 direct RSS observations and upstream totals.")


if __name__ == "__main__":
    main()
