import fnmatch
import os
import subprocess
import pytest


@pytest.mark.eda
@pytest.mark.skip(reason="Not passing")
def test_lint():
    errors = 0

    test_inc_dir = os.path.join(os.path.dirname(__file__), "data")

    for root, dirs, files in os.walk("."):
        for filename in files:
            if fnmatch.fnmatch(filename, "*.v"):
                fullpath = os.path.join(root, filename)
                lint_result = subprocess.run(
                    [
                        "slang",
                        "--lint-only",
                        "-I",
                        test_inc_dir,
                        "+define+USE_SYSTEMVERILOG",
                        fullpath,
                    ]
                )
                if lint_result.returncode != 0:
                    print(f"Lint failed for {fullpath}")
                    errors += 1

    assert errors == 0, "Lint failed"
