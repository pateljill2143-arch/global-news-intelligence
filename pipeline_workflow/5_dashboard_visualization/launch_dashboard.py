"""
STEP 5: LAUNCH DASHBOARD VISUALIZATION
Modes:
  python launch_dashboard.py          -> local  (http://localhost:8501)
  python launch_dashboard.py --share  -> public ngrok link you can share with friends
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

DASHBOARD_FILE = Path(__file__).parent.parent.parent / "dashboard.py"
STREAMLIT_PORT = 8501


def _ensure_pyngrok():
    """Install pyngrok silently if it is not available."""
    try:
        import pyngrok  # noqa: F401
    except ImportError:
        print("Installing pyngrok …")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyngrok", "--quiet"],
            check=True,
        )


def launch_local():
    """Start Streamlit and block until the user presses Ctrl+C."""
    print("=" * 80)
    print("STEP 5: LAUNCHING DASHBOARD (LOCAL)")
    print("=" * 80)
    print()
    print("Dashboard will show:")
    print("  Collected articles from APIs and the Internet")
    print("  Data stored in MongoDB")
    print("  Entities extracted with BERT NER")
    print("  Relationships built in Neo4j")
    print("  Interactive knowledge graph visualization")
    print()
    print("Opening dashboard in browser ...")
    print("  URL: http://localhost:8501")
    print()
    print("Press Ctrl+C to stop the dashboard")
    print("=" * 80)
    print()
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(DASHBOARD_FILE)]
    )


def launch_shared():
    """Start Streamlit in a background thread, then open an ngrok tunnel."""
    _ensure_pyngrok()
    from pyngrok import ngrok  # noqa: E402

    print("=" * 80)
    print("STEP 5: LAUNCHING DASHBOARD (SHARE MODE)")
    print("=" * 80)
    print()
    print("Starting Streamlit server in the background …")

    # Run Streamlit in a daemon thread so it dies when this script exits
    def _run_streamlit():
        subprocess.run(
            [
                sys.executable, "-m", "streamlit", "run", str(DASHBOARD_FILE),
                "--server.port", str(STREAMLIT_PORT),
                "--server.headless", "true",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    t = threading.Thread(target=_run_streamlit, daemon=True)
    t.start()

    # Give Streamlit a moment to bind to its port
    print("Waiting for server to start …")
    time.sleep(5)

    # Open ngrok tunnel
    print("Opening ngrok tunnel …")
    public_url = ngrok.connect(STREAMLIT_PORT)
    print()
    print("=" * 80)
    print("  PUBLIC URL (share this with your friends):")
    print(f"  {public_url}")
    print("=" * 80)
    print()
    print("Press Ctrl+C to stop sharing and shut down the server.")
    print()

    try:
        # Keep the process alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down …")
        ngrok.disconnect(public_url)
        ngrok.kill()


def main():
    if "--share" in sys.argv:
        launch_shared()
    else:
        launch_local()


if __name__ == "__main__":
    main()
