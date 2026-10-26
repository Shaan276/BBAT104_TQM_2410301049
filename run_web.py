"""
Web Application Runner
Project: Online Quiz System [Q05: Reduce Response Time]
Gamified Kahoot & Quizizz Interface (React + Node.js + SQLite)
Student: Piyush Pilkhwal (2410301049) | Course: BBAT104 TQM
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
WEB_DIR = ROOT_DIR / "web"
BACKEND_DIR = WEB_DIR / "backend"
FRONTEND_DIR = WEB_DIR / "frontend"
DIST_DIR = FRONTEND_DIR / "dist"

def main():
    print("=" * 70)
    print("  🚀 QuizTQM Gamified Web Arena (Kahoot & Quizizz Inspired)")
    print("  Quality Goal: Q05 [Reduce Response Time] | TQM Course BBAT104")
    print("  Student: Piyush Pilkhwal (2410301049)")
    print("=" * 70)

    # 1. Verify Node.js
    try:
        node_ver = subprocess.check_output(["node", "-v"], text=True).strip()
        print(f"  [✓] Node.js Runtime detected: {node_ver}")
    except Exception:
        print("  [✗] Error: Node.js is not found in PATH. Please install Node.js.")
        sys.exit(1)

    # 2. Check if frontend build exists
    if not (DIST_DIR / "index.html").exists():
        print("  [*] Frontend build not found. Building React client now...")
        subprocess.run(["npm", "run", "build"], cwd=str(FRONTEND_DIR), check=True, shell=True)
        print("  [✓] React frontend built successfully!")
    else:
        print("  [✓] Production React frontend build is ready.")

    port = 5000
    url = f"http://localhost:{port}"

    print(f"\n  [★] Launching Server on {url}")
    print("  [*] Opening browser in 2 seconds...")
    print("  [*] Press Ctrl+C in this terminal to stop the web app.\n")

    # Open browser after slight delay
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run Node backend server
    try:
        subprocess.run(["node", "server.js"], cwd=str(BACKEND_DIR), check=True, shell=True)
    except KeyboardInterrupt:
        print("\n  [*] Web server stopped. Have a great day!")

if __name__ == "__main__":
    main()
