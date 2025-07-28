# run_tests.py
import os
import subprocess

output_file = "tests/report.md"
os.makedirs(os.path.dirname(output_file), exist_ok=True)

print("🔍 Running tests...")

result = subprocess.run(
    ["pytest", "tests", "--md-report", output_file],
    capture_output=True,
    text=True
)

print(result.stdout)

if result.returncode == 0:
    print("✅ All tests passed.")
else:
    print("❌ Some tests failed.")

if os.path.exists(output_file):
    print(f"📄 Markdown report saved to: {output_file}")
else:
    print("⚠️ Markdown report was NOT created. Check if `pytest-md-report` is installed.")
