#!/usr/bin/env python3
"""Cold-build the four frozen sources and record a matched two-bank benchmark."""

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile


ARCHIVE = Path(__file__).resolve().parents[1]
REPO = ARCHIVE.parent
FLAGS = ("-O2", "-std=c++17", "-pipe", "-DNDEBUG")
METHODS = {
    "Z1": (
        "Stage 2 Formal Report/UFUG2106_Final_Algorithm_Audit_v1/"
        "stage1_zeyun/UFUG2106_Stage1/src/synth.cpp"
    ),
    "J51": "Stage1_Freeze_Round5.1_Verified/source_snapshot/src/synth_round51.cpp",
    "R10.0": "UFUG2106_Round10_0_Delivery/submission/synth.cpp",
    "Integrated Final": f"{ARCHIVE.name}/src/synth_stage2.cpp",
}
BANKS = ("stage1", "stage2")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def run_logged(command, log, *, cwd=None, accepted=(0,)):
    with log.open("w", encoding="utf-8") as stream:
        result = subprocess.run(command, cwd=cwd, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode not in accepted:
        result.check_returncode()
    return result.returncode


def public_cases(work):
    cases = {}
    for bank in BANKS:
        cases[bank] = sorted((work / "data" / bank).glob("case_*.txt"))
        expected = [f"case_{n:03d}.txt" for n in range(1, 26)]
        if [p.name for p in cases[bank]] != expected:
            raise ValueError(f"{bank}: expected exactly case_001.txt through case_025.txt")
    return cases


def build(work, logs):
    cold = work / "cold_archive"
    cold.mkdir()
    for folder in ("src", "releases", "tests", "tools", "examples"):
        shutil.copytree(ARCHIVE / folder, cold / folder, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copyfile(ARCHIVE / "Makefile", cold / "Makefile")
    run_logged(["make", "stage2", "stage2-source"], logs / "cold-build.txt", cwd=cold)
    bundle = cold / "artifacts/UFUG2106_Group2_Stage2_Source.zip"
    extracted = work / "extracted_release"
    with ZipFile(bundle) as archive:
        archive.extractall(extracted)
    run_logged(
        ["g++", "-O2", "-std=c++17", "synth_stage2.cpp", "-o", "synth"],
        logs / "source-package-build.txt", cwd=extracted,
    )
    for base, name in ((cold / "build", "synth_stage2"), (extracted, "synth")):
        example = cold / "examples/shared_outputs.txt"
        netlist = base / "smoke.net"
        run_logged([base / name, example, netlist], logs / f"{name}-smoke.txt")
        run_logged(
            [sys.executable, cold / "tools/check_circuit.py", example, netlist],
            logs / f"{name}-smoke-verified.txt",
        )

    binaries = {}
    source_hashes = {}
    for method, relative in METHODS.items():
        label = method.replace(" ", "_")
        src = REPO / relative
        snapshot = work / f"compile_{label}"
        snapshot.mkdir()
        files = [src, *sorted(src.parent.glob("*.hpp"))]
        if method == "Integrated Final":
            files.extend(sorted((src.parent / "round51").glob("*.hpp")))
        source_hashes[method] = {}
        for path in files:
            dest = snapshot / path.relative_to(src.parent)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
            source_hashes[method][path.relative_to(REPO).as_posix()] = sha256(dest)
        binaries[method] = snapshot / "synth"
        run_logged(["g++", *FLAGS, src.name, "-o", "synth"], logs / f"matched-{label}-build.txt",
                   cwd=snapshot)
    return binaries, source_hashes


def measure_evaluator(work, output, binaries, cases):
    schedule = []
    replays = []
    for repeat in (1, 2):
        methods = list(binaries) if repeat == 1 else list(reversed(binaries))
        banks = BANKS if repeat == 1 else BANKS[::-1]
        for bank in banks:
            for method in methods:
                name = f"r{repeat}_{bank}_{method.replace(' ', '_')}"
                print(f"Evaluator {name}", flush=True)
                report = output / "official" / f"{name}.csv"
                circuits = work / name
                exit_code = run_logged([
                    work / "evaluator", binaries[method], cases[bank][0].parent,
                    "--report", report, "--save-outputs", circuits,
                ], output / "logs" / f"{name}.txt", accepted=(0, 1))
                with report.open(newline="", encoding="utf-8") as stream:
                    rows = list(csv.DictReader(stream))
                if sorted(row["case"] for row in rows) != [p.name for p in cases[bank]]:
                    raise ValueError(f"Incomplete evaluator report: {name}")
                if bool(exit_code) != any(row["status"] != "PASS" for row in rows):
                    raise ValueError(f"Evaluator exit status disagrees with its CSV: {name}")
                schedule.append({"repeat": repeat, "bank": bank, "method": method,
                                 "evaluator_exit_code": exit_code,
                                 "report": report.relative_to(output).as_posix()})
                if method == "Integrated Final":
                    replays.append((name, cases[bank][0].parent, report, circuits))
    return schedule, replays


def measure_memory(work, output, binaries, cases):
    scratch = work / "rss"
    scratch.mkdir()
    with (output / "direct_memory.csv").open("w", newline="", encoding="utf-8") as stream:
        w = csv.writer(stream, lineterminator="\n")
        w.writerow(("method", "bank", "case", "exit_code", "peak_rss_kib"))
        for bank, inputs in cases.items():
            for method, binary in binaries.items():
                print(f"Direct RSS {bank} {method}", flush=True)
                for case in inputs:
                    netlist, rss = scratch / "netlist", scratch / "rss_kib"
                    netlist.unlink(missing_ok=True)
                    rss.unlink(missing_ok=True)
                    # A fresh directly launched process for each case. No evaluator limits.
                    result = subprocess.run(
                        ["/usr/bin/time", "-f", "%M", "-o", rss, binary, case, netlist],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90,
                    )
                    w.writerow((method, bank, case.name, result.returncode,
                                int(rss.read_text().splitlines()[-1])))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New directory for CSVs and run evidence")
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True)
    for subdir in ("official", "independent", "logs"):
        (output / subdir).mkdir()
    started = datetime.now(timezone.utc)
    with tempfile.TemporaryDirectory(prefix="ufug-final-integration-") as folder:
        work = Path(folder)
        shutil.copytree(REPO / "data", work / "data")
        shutil.copyfile(REPO / "evaluator", work / "evaluator")
        (work / "evaluator").chmod(0o755)
        cases = public_cases(work)
        print("Cold-building the standalone release and four matched executables", flush=True)
        binaries, source_hashes = build(work, output / "logs")
        environment = {
            "started_utc": started.isoformat(),
            "platform": platform.platform(),
            "libc": platform.libc_ver(),
            "cpu": next(line.split(":", 1)[1].strip() for line in
                        Path("/proc/cpuinfo").read_text().splitlines()
                        if line.startswith("model name")),
            "compiler": subprocess.check_output(["g++", "--version"], text=True).splitlines()[0],
            "python": platform.python_version(),
            "numpy": subprocess.check_output(
                [sys.executable, "-c", "import numpy; print(numpy.__version__)"], text=True
            ).strip(),
            "compiler_flags": list(FLAGS),
            "evaluator_sha256": sha256(work / "evaluator"),
            "input_sha256": {f"{bank}/{case.name}": sha256(case)
                             for bank, paths in cases.items() for case in paths},
            "source_sha256": source_hashes,
            "public_runs": "Sequential official evaluations with default input limits and saved outputs.",
            "direct_memory_runs": "Separate uncapped Linux process starts, GNU time %M (KiB).",
        }
        write_json(output / "environment.json", environment)
        schedule, replays = measure_evaluator(work, output, binaries, cases)
        environment["run_order"] = schedule
        write_json(output / "environment.json", environment)
        for name, bank, report, circuits in replays:
            print(f"Exhaustive replay {name}", flush=True)
            run_logged(
                [sys.executable, ARCHIVE / "tools/verify_all.py", bank, circuits,
                 report, output / "independent" / f"{name}.json"],
                output / "logs" / f"{name}-independent.txt",
            )
        measure_memory(work, output, binaries, cases)
        environment["finished_utc"] = datetime.now(timezone.utc).isoformat()
        write_json(output / "environment.json", environment)


if __name__ == "__main__":
    main()
