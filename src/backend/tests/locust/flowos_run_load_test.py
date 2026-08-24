#!/usr/bin/env python3
"""FlowOS Load Test Runner

This script provides an easy way to run FlowOS load tests.
For first-time setup, use setup_flowos_test.py to create test credentials.

Usage:
    # First time setup (run once):
    python setup_flowos_test.py --interactive

    # Then run load tests:
    python run_load_test.py --help
    python run_load_test.py --users 10 --duration 60
    python run_load_test.py --shape ramp100 --host http://localhost:7860
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd, check=True, capture_output=False):
    """Run a shell command with proper error handling."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, check=check)
            return result.stdout.strip()
        subprocess.run(cmd, shell=isinstance(cmd, str), check=check)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        if capture_output and e.stdout:
            print(f"STDOUT: {e.stdout}")
        if capture_output and e.stderr:
            print(f"STDERR: {e.stderr}")
        if check:
            sys.exit(1)


def check_flowos_running(host):
    """Check if FlowOS is already running."""
    try:
        import httpx

        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{host}/health")
            return response.status_code == 200
    except Exception:
        return False


def test_single_request(host):
    """Test a single flow request to ensure the setup works before load testing."""
    import os

    import httpx

    api_key = os.getenv("API_KEY")
    flow_id = os.getenv("FLOW_ID")

    if not api_key or not flow_id:
        print("⚠️  Missing API_KEY or FLOW_ID for test request")
        return False

    print("\n🧪 Testing single request before load test...")
    print(f"   Flow ID: {flow_id}")
    print(f"   API Key: {api_key[:20]}...")

    # First, test basic connectivity
    print("   🔗 Testing basic connectivity...")
    try:
        with httpx.Client(timeout=10.0) as client:
            health_response = client.get(f"{host}/health")
            if health_response.status_code == 200:
                print("   ✅ Health check passed")
            else:
                print(f"   ⚠️  Health check failed: {health_response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Connectivity test failed: {e}")
        print(f"      Error type: {type(e).__name__}")
        return False

    # Now test the actual flow request
    print("   🎯 Testing flow request...")
    try:
        url = f"{host}/api/v1/run/{flow_id}?stream=false"
        payload = {
            "input_value": "Hello, this is a test message",
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {},
        }
        headers = {"x-api-key": api_key, "Content-Type": "application/json"}

        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)

            print(f"   📡 Response status: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("outputs"):
                        print("   ✅ Test request successful - flow is working!")
                        return True
                    print(f"   ⚠️  Flow executed but no outputs returned: {data}")
                    return False
                except Exception as e:
                    print(f"   ⚠️  Invalid JSON response: {e}")
                    return False
            else:
                print(f"   ❌ Test request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False

    except Exception as e:
        print(f"   ❌ Test request error: {e}")
        return False


def wait_for_flowos(host, timeout=60):
    """Wait for FlowOS to be ready."""
    print(f"Waiting for FlowOS to be ready at {host}...")
    start_time = time.time()

    while time.time() - start_time < timeout:
        if check_flowos_running(host):
            print("✅ FlowOS is ready!")
            return True
        time.sleep(2)

    print(f"❌ FlowOS did not start within {timeout} seconds")
    return False


def start_flowos(host, port):
    """Start FlowOS server if not already running."""
    if check_flowos_running(host):
        print(f"✅ FlowOS is already running at {host}")
        return None

    print(f"Starting FlowOS server on port {port}...")

    # Start FlowOS in the background
    cmd = [
        sys.executable,
        "-m",
        "flowos",
        "run",
        "--host",
        "0.0.0.0",
        "--port",
        str(port),
        "--auto-login",
        "--log-level",
        "warning",
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for it to be ready
    if wait_for_flowos(host, timeout=60):
        return process
    process.terminate()
    return None


def run_locust_test(args):
    """Run the Locust load test."""
    locust_file = Path(__file__).parent / "flowos_locustfile.py"

    # Check for required environment variables
    if not os.getenv("API_KEY"):
        print("❌ API_KEY environment variable not found!")
        print("Run flowos_setup_test.py first to create test credentials.")
        sys.exit(1)

    if not os.getenv("FLOW_ID"):
        print("❌ FLOW_ID environment variable not found!")
        print("Run flowos_setup_test.py first to create test credentials.")
        sys.exit(1)

    cmd = [
        "locust",
        "-f",
        str(locust_file),
        "--host",
        args.host,
    ]

    # Add shape if specified
    env = os.environ.copy()
    if args.shape:
        env["SHAPE"] = args.shape

    # Add other environment variables
    env["FLOWOS_HOST"] = args.host

    if args.headless:
        cmd.extend(
            [
                "--headless",
                "--users",
                str(args.users),
                "--spawn-rate",
                str(args.spawn_rate),
                "--run-time",
                f"{args.duration}s",
            ]
        )

    if args.csv:
        cmd.extend(["--csv", args.csv])

    if args.html:
        cmd.extend(["--html", args.html])

    print(f"\n{'=' * 60}")
    print("STARTING LOAD TEST")
    print(f"{'=' * 60}")
    print(f"Command: {' '.join(cmd)}")
    print(f"Host: {args.host}")
    print(f"Users: {args.users}")
    print(f"Duration: {args.duration}s")
    print(f"Shape: {args.shape or 'default'}")
    print(f"API Key: {env.get('API_KEY', 'N/A')[:20]}...")
    print(f"Flow ID: {env.get('FLOW_ID', 'N/A')}")
    if args.html:
        print(f"HTML Report: {args.html}")
    if args.csv:
        print(f"CSV Reports: {args.csv}_*.csv")
    print(f"{'=' * 60}\n")

    subprocess.run(cmd, check=False, env=env)


def main():
    parser = argparse.ArgumentParser(
        description="Run FlowOS load tests with automatic setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with web UI (interactive)
  python run_load_test.py

  # Run headless test with 50 users for 2 minutes
  python run_load_test.py --headless --users 50 --duration 120

  # Run with specific load shape
  python run_load_test.py --shape ramp100 --headless --users 100 --duration 180

  # Run against existing FlowOS instance
  python run_load_test.py --host http://localhost:8000 --no-start-flowos

  # Save results to CSV
  python run_load_test.py --headless --csv results --users 25 --duration 60
        """,
    )

    # FlowOS options
    parser.add_argument(
        "--host",
        default="http://localhost:7860",
        help="FlowOS host URL (default: http://localhost:7860, use https:// for remote instances)",
    )
    parser.add_argument("--port", type=int, default=7860, help="Port to start FlowOS on (default: 7860)")
    parser.add_argument(
        "--no-start-flowos",
        action="store_true",
        help="Don't start FlowOS automatically (assume it's already running)",
    )

    # Load test options
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no web UI)")
    parser.add_argument("--users", type=int, default=50, help="Number of concurrent users (default: 20)")
    parser.add_argument(
        "--spawn-rate", type=int, default=2, help="Rate to spawn users at (users per second, default: 2)"
    )
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (default: 60)")
    parser.add_argument("--shape", choices=["ramp100", "stepramp"], help="Load test shape to use")
    parser.add_argument("--csv", help="Save results to CSV files with this prefix")
    parser.add_argument("--html", help="Generate HTML report with this filename (e.g., report.html)")

    args = parser.parse_args()

    # Check dependencies
    try:
        import httpx
        import locust
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Install with: pip install locust httpx")
        sys.exit(1)

    flowos_process = None

    try:
        # Start FlowOS if needed
        if not args.no_start_flowos:
            if args.host.startswith("https://") or not args.host.startswith("http://localhost"):
                print(f"⚠️  Remote host detected: {args.host}")
                print("   For remote instances, use --no-start-flowos flag")
                print("   Example: --host https://your-remote-instance.com --no-start-flowos")
                sys.exit(1)

            flowos_process = start_flowos(args.host, args.port)
            if not flowos_process:
                print("❌ Failed to start FlowOS")
                sys.exit(1)
        # Just check if it's running
        elif not check_flowos_running(args.host):
            print(f"❌ FlowOS is not running at {args.host}")
            if args.host.startswith("https://"):
                print("   Make sure your remote FlowOS instance is accessible")
            else:
                print("Either start FlowOS manually or remove --no-start-flowos flag")
            sys.exit(1)
        else:
            print(f"🔗 Using existing FlowOS instance at {args.host}")
            if args.host.startswith("https://"):
                print("   ✅ Remote instance mode")

        # Test a single request before running the full load test
        if not test_single_request(args.host):
            print("❌ Single request test failed. Aborting load test.")
            sys.exit(1)

        # Run the load test
        run_locust_test(args)

    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        # Clean up FlowOS process
        if flowos_process:
            print("\nStopping FlowOS server...")
            flowos_process.terminate()
            try:
                flowos_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                flowos_process.kill()
            print("✅ FlowOS server stopped")


if __name__ == "__main__":
    main()
