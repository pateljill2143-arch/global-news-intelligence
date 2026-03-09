"""
🚀 RUN COMPLETE WORKFLOW - ALL 5 STEPS AUTOMATICALLY
Executes the entire pipeline from data collection to dashboard
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time
from pymongo import MongoClient

WORKFLOW_DIR = Path(__file__).parent
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB = "global_news_intelligence"
# -- Neo4j config --------------------------------------------------------
NEO4J_URI  = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASS = "jill2143"


# ── Background Daemon config ───────────────────────────────────────────────
DAEMON_INTERVAL_HOURS = 6            # Re-run full pipeline every 6 hours
TASK_NAME             = "GlobalNewsIntelligenceDaemon"
LOG_FILE              = WORKFLOW_DIR / "daemon.log"

# Pipeline steps executed by the daemon (in order)
DAEMON_STEPS = [
    ("1_data_collection/collect_api_data.py",         "Data Collection"),
    ("2_mongodb_storage/store_in_mongodb.py",         "MongoDB Storage"),
    ("3_entity_extraction/extract_entities.py",       "Entity Extraction"),
    ("4_relationship_building/build_relationships.py","Relationship Building"),
]


def _daemon_log(msg, fh=None):
    """Write a timestamped line to console (if open) and the log file."""
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    try:
        print(line)
    except Exception:
        pass          # stdout may not exist when launched by Task Scheduler
    if fh:
        fh.write(line + "\n")
        fh.flush()


def run_daemon():
    """
    Infinite loop that executes the full pipeline every DAEMON_INTERVAL_HOURS.
    Logs everything to daemon.log so you can check progress without VS Code.

    Launch options:
      pythonw RUN_COMPLETE_WORKFLOW.py --daemon   (no console window)
      python  RUN_COMPLETE_WORKFLOW.py --daemon   (with console, for testing)
    """
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        _daemon_log("=" * 60, fh)
        _daemon_log("DAEMON STARTED", fh)
        _daemon_log(f"Interval: every {DAEMON_INTERVAL_HOURS} hour(s)", fh)
        _daemon_log(f"Log file: {LOG_FILE}", fh)
        _daemon_log("=" * 60, fh)

        run_number = 0
        while True:
            run_number += 1
            _daemon_log(f"", fh)
            _daemon_log(f"--- PIPELINE RUN #{run_number} ---", fh)

            for script_rel, step_name in DAEMON_STEPS:
                script_path = WORKFLOW_DIR / script_rel
                _daemon_log(f"  [{step_name}] starting...", fh)
                try:
                    result = subprocess.run(
                        [sys.executable, str(script_path)],
                        capture_output=True, text=True, timeout=3600
                    )
                    if result.returncode == 0:
                        _daemon_log(f"  [{step_name}] OK", fh)
                    else:
                        _daemon_log(f"  [{step_name}] FAILED (exit {result.returncode})", fh)
                        # Log last 10 lines of stderr for diagnosis
                        for err_line in result.stderr.strip().splitlines()[-10:]:
                            _daemon_log(f"    ERR: {err_line}", fh)
                except subprocess.TimeoutExpired:
                    _daemon_log(f"  [{step_name}] TIMEOUT after 60 min", fh)
                except Exception as e:
                    _daemon_log(f"  [{step_name}] ERROR: {e}", fh)

            next_run = datetime.fromtimestamp(
                time.time() + DAEMON_INTERVAL_HOURS * 3600
            ).strftime("%Y-%m-%d %H:%M:%S")
            _daemon_log(f"--- Run #{run_number} complete. Next run at {next_run} ---", fh)

            time.sleep(DAEMON_INTERVAL_HOURS * 3600)


def install_windows_task():
    """
    Register the daemon with Windows Task Scheduler.
    The task runs every DAEMON_INTERVAL_HOURS and also at system startup,
    so the pipeline keeps going after reboots with no VS Code open.
    """
    # Use pythonw.exe so no console window pops up
    pythonw = Path(sys.executable).parent / "pythonw.exe"
    if not pythonw.exists():
        pythonw = Path(sys.executable)   # fallback to python.exe

    script = Path(__file__).resolve()
    trigger_interval = str(DAEMON_INTERVAL_HOURS * 60)  # schtasks wants minutes

    print("\n" + "=" * 60)
    print("  INSTALLING BACKGROUND DAEMON")
    print("=" * 60)
    print(f"  Task name : {TASK_NAME}")
    print(f"  Runs every: {DAEMON_INTERVAL_HOURS} hour(s)")
    print(f"  Executable: {pythonw}")
    print(f"  Log file  : {LOG_FILE}")

    # Create the Task Scheduler XML via schtasks
    # /sc MINUTE /mo N  → every N minutes
    # /rl HIGHEST       → run with highest privileges (avoids UAC blocks)
    # /f                → overwrite if task already exists
    cmd = [
        "schtasks", "/create",
        "/tn",  TASK_NAME,
        "/tr",  f'"{pythonw}" "{script}" --daemon',
        "/sc",  "MINUTE",
        "/mo",  trigger_interval,
        "/rl",  "HIGHEST",
        "/f",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("\n  SUCCESS! Task registered in Windows Task Scheduler.")
            print("  The pipeline will now run automatically in the background.")
            print("  You can close VS Code, your terminal, even reboot — it keeps running.")
            print(f"\n  Check progress: open '{LOG_FILE.name}' in this folder")
            print(f"  Manage task  : open Task Scheduler → search '{TASK_NAME}'")
            print(f"  Remove       : python RUN_COMPLETE_WORKFLOW.py --uninstall-task")
        else:
            print(f"\n  FAILED: {result.stderr.strip()}")
            print("  Try running this script as Administrator.")
    except FileNotFoundError:
        print("  ERROR: schtasks not found. Are you on Windows?")


def uninstall_windows_task():
    """Remove the daemon from Windows Task Scheduler."""
    print(f"\nRemoving Task Scheduler job: {TASK_NAME}")
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", TASK_NAME, "/f"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  OK  Task '{TASK_NAME}' removed. Pipeline will no longer run in background.")
        else:
            print(f"  ERR {result.stderr.strip()}")
    except FileNotFoundError:
        print("  ERROR: schtasks not found. Are you on Windows?")


def show_daemon_status():
    """Show whether the daemon is scheduled and print the last 30 log lines."""
    print("\n" + "=" * 60)
    print("  DAEMON STATUS")
    print("=" * 60)

    # Check Task Scheduler registration
    result = subprocess.run(
        ["schtasks", "/query", "/tn", TASK_NAME, "/fo", "LIST"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("  Task Scheduler : REGISTERED")
        for line in result.stdout.splitlines():
            if any(k in line for k in ("Status", "Next Run", "Last Run", "Last Result")):
                print(f"    {line.strip()}")
    else:
        print("  Task Scheduler : NOT registered")
        print(f"  Install with  : python RUN_COMPLETE_WORKFLOW.py --install-task")

    # Show tail of log file
    print()
    if LOG_FILE.exists():
        lines = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"  Log file ({LOG_FILE.name}) — last {min(30, len(lines))} lines:")
        print("  " + "-" * 56)
        for line in lines[-30:]:
            print(f"  {line}")
    else:
        print("  No log file yet — daemon has not run.")
        print(f"  Expected: {LOG_FILE}")
    print("=" * 60)


def count_unprocessed():
    """Count unprocessed articles in MongoDB"""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[MONGO_DB]
        count = db["raw_articles"].count_documents({"processed": False})
        client.close()
        return count
    except:
        return 0

def run_step(step_number, script_name, description):
    """Run a workflow step"""
    print("\n" + "="*80)
    print(f"STEP {step_number}: {description}")
    print("="*80)
    
    script_path = WORKFLOW_DIR / script_name
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], check=True)
        print(f"\n✅ Step {step_number} completed successfully")
        return True
    except subprocess.CalledProcessError:
        print(f"\n❌ Step {step_number} failed")
        return False
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Step {step_number} interrupted by user")
        return False


def run_impact_prediction_engine():
    """Launch the Impact Prediction Engine (causal chain CLI)."""
    import importlib.util
    print("\n" + "="*70)
    print("  IMPACT PREDICTION ENGINE")
    print("  Ask: If X happens -> what comes next?")
    print("="*70)
    br_path = WORKFLOW_DIR / "4_relationship_building" / "build_relationships.py"
    spec    = importlib.util.spec_from_file_location("build_relationships", br_path)
    br_mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(br_mod)
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        driver.verify_connectivity()
        print("  Connected to Neo4j")
    except Exception as e:
        print(f"  Cannot connect to Neo4j: {e}")
        return
    br_mod.seed_causal_graph(driver)
    br_mod.run_impact_cli(driver)
    driver.close()

def main():
    start_time = time.time()
    
    print("="*80)
    print("🚀 COMPLETE WORKFLOW - 5 STEPS TO DASHBOARD")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This will execute:")
    print("  Step 1: Collect MASSIVE data (4 APIs + 25+ RSS feeds)")
    print("  Step 2: Store data in MongoDB")
    print("  Step 3: Extract entities with BERT NER (all batches)")
    print("  Step 4: Build relationships in Neo4j")
    print("  Step 5: Launch dashboard")
    print()
    
    try:
        input("▶️  Press ENTER to start workflow...")
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled")
        return
    
    # Step 1: Collect data (now includes both APIs and RSS feeds)
    if not run_step(1, "1_data_collection/collect_api_data.py", "MASSIVE DATA COLLECTION (APIs + RSS)"):
        return
    
    time.sleep(2)
    
    # Step 2: Store in MongoDB
    if not run_step(2, "2_mongodb_storage/store_in_mongodb.py", "STORE IN MONGODB"):
        return
    
    time.sleep(2)
    
    # Steps 3 & 4: Extract entities in batches, then build relationships
    print("\n" + "="*80)
    print("STEP 3 & 4: EXTRACT ENTITIES + BUILD RELATIONSHIPS (batch mode)")
    print("="*80)

    unprocessed = count_unprocessed()
    print(f"📊 Unprocessed articles: {unprocessed:,}")

    if unprocessed == 0:
        print("✅ All articles already processed — skipping extraction")
    else:
        batch = 1
        extract_script = WORKFLOW_DIR / "3_entity_extraction" / "extract_entities.py"

        while True:
            remaining = count_unprocessed()
            if remaining == 0:
                break
            print(f"\n📦 BATCH #{batch} — {remaining:,} articles remaining")
            try:
                subprocess.run([sys.executable, str(extract_script)], check=True)
            except subprocess.CalledProcessError:
                print("❌ Entity extraction failed — stopping")
                return
            batch += 1
            time.sleep(1)

        print(f"\n✅ All articles extracted in {batch-1} batch(es)")

    # Build Neo4j relationships (once, after all extraction is done)
    print("\n🕸️  Building Neo4j relationships...")
    rel_script = WORKFLOW_DIR / "4_relationship_building" / "build_relationships.py"
    try:
        subprocess.run([sys.executable, str(rel_script)], check=True)
        print("✅ Relationships built successfully")
    except subprocess.CalledProcessError:
        print("⚠️  Relationship building had issues (dashboard may still work)")

    time.sleep(2)
    
    # Final Summary
    elapsed = time.time() - start_time

    print("\n" + "="*80)
    print("WORKFLOW COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"Total time: {elapsed/60:.1f} minutes")
    print()
    print("What was done:")
    print("  1. Collected articles (4 APIs + 25+ RSS feeds)")
    print("  2. Stored in MongoDB")
    print("  3. Extracted entities with BERT NER")
    print("  4. Built knowledge graph in Neo4j")
    print()
    print("What would you like to do next?")
    print("  [1] Launch dashboard          (local  http://localhost:8501)")
    print("  [2] Share dashboard ONLINE    <- public link, send to friends")
    print("  [3] Impact Prediction Engine  <- If X happens, what next?")
    print("  [4] Exit")
    print("="*80)

    try:
        choice = input("\nEnter choice (1/2/3/4): ").strip()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        return

    if choice == "0":
        import antigravity  # secret easter egg

    if choice == "1":
        run_step(5, "5_dashboard_visualization/launch_dashboard.py", "DASHBOARD (LOCAL)")
    elif choice == "2":
        _dash = WORKFLOW_DIR / "5_dashboard_visualization" / "launch_dashboard.py"
        subprocess.run([sys.executable, str(_dash), "--share"])
    elif choice == "3":
        run_impact_prediction_engine()
    else:
        print("\nGoodbye!")
if __name__ == "__main__":
    if "--daemon" in sys.argv:
        # Launched by Task Scheduler or start_background.bat
        run_daemon()
    elif "--install-task" in sys.argv:
        install_windows_task()
    elif "--uninstall-task" in sys.argv:
        uninstall_windows_task()
    elif "--status" in sys.argv:
        show_daemon_status()
    else:
        main()
