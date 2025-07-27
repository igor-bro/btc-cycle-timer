import subprocess
import os

output_file = "tests/report.md"

# Ensure output directory exists
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Run pytest with markdown plugin and output to file
result = subprocess.run(
    ["pytest", "tests/", "--md-report", output_file],
    capture_output=True,
    text=True
)

print("✅ Done")
print("ℹ️ Saved to:", output_file)
print(result.stdout)
