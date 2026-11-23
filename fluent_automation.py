"""Config-driven Fluent 2025 automation. Run --check before execution."""
import argparse
import json
from pathlib import Path
from datetime import datetime

def load(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8-sig"))
    base = path.parent
    mode = cfg.get("mode", "solver")
    if mode not in ("solver", "meshing"):
        raise ValueError("mode must be solver or meshing")
    for key in ("case", "journal"):
        if cfg.get(key):
            p = (base / cfg[key]).resolve()
            if not p.is_file():
                raise ValueError(f"Missing {key}: {p}")
            cfg[key] = str(p)
    if mode == "meshing" and not cfg.get("journal"):
        raise ValueError("Meshing requires a geometry-specific Fluent journal")
    if mode == "solver" and not cfg.get("case"):
        raise ValueError("Solver requires an existing case")
    if not isinstance(cfg.get("cores", 2), int) or cfg.get("cores", 2) < 1:
        raise ValueError("cores must be a positive integer")
    n = cfg.get("iterations", 0)
    if not isinstance(n, int) or n < 0:
        raise ValueError("iterations must be a nonnegative integer")
    if mode == "meshing" and (n or cfg.get("settings")):
        raise ValueError("Use a separate solver config for settings and iterations")
    cfg["output_root"] = str((base / cfg.get("output_root", "../runs")).resolve())
    return cfg

def run(cfg):
    import ansys.fluent.core as pyfluent
    out = Path(cfg["output_root"]) / datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    out.mkdir(parents=True, exist_ok=False)
    session = None
    try:
        session = pyfluent.launch_fluent(
            product_version=cfg.get("version", "25.2"),
            mode=cfg.get("mode", "solver"), precision="double",
            dimension=cfg.get("dimension", 3), processor_count=cfg.get("cores", 2),
            cwd=str(out), start_timeout=120)
        session.transcript.start(file_name=str(out / "fluent.log"))
        if cfg.get("case"):
            session.settings.file.read_case(file_name=cfg["case"])
        if cfg.get("journal"):
            session.tui.file.read_journal(cfg["journal"])
        if cfg.get("mode", "solver") == "solver":
            # Native Fluent settings tree: models, materials, boundary_conditions,
            # methods, controls, monitors. Invalid names fail rather than being skipped.
            if cfg.get("settings"):
                session.settings.set_state(cfg["settings"])
            if cfg.get("initialize", False):
                session.settings.solution.initialization.hybrid_initialize()
            if cfg.get("iterations", 0):
                session.settings.solution.run_calculation.iterate(
                    iter_count=cfg["iterations"])
            session.settings.file.write_case_data(file_name=str(out / "result.cas.h5"))
        (out / "completed.json").write_text(
            json.dumps({"status": "completed", "config": cfg}, indent=2),
            encoding="utf-8")
        print(out)
    finally:
        if session is not None:
            session.exit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("--check", action="store_true",
                        help="Validate inputs without starting Fluent")
    args = parser.parse_args()
    cfg = load(args.config)
    if args.check:
        print(json.dumps(cfg, indent=2))
    else:
        run(cfg)

if __name__ == "__main__":
    main()
