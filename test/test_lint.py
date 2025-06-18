
import fnmatch
import os
import subprocess
import pytest

# Test that any RTL in the repo can pass a slang-based lint
# check.  There are a couple of dirty tricks that are needed
# to make this test generic:
#
# 1.  To deal with includes, it is necessary to provide include
#     paths to files that need them.  In general, use of includes
#     in this repo should be kept to an absolute minimum.  As of
#     the implementation of this test, the only include that is
#     used is in a top-level testbench to include the DUT.  We
#     provide an empty include here and the path to it so that
#     the rest of the file can be run through lint properly.
# 2.  In rare cases code may be Verilog-2005 compatible and cause
#     lint errors.  This is known to occur in the matrix multiply
#     testbench, where pyslang complains that the filename variables
#     should be strings instead of large reg variables.
#     To resolve this, a USE_SYSTEMVERILOG `ifdef wrapper is employed
#     so that developers can create a lint-free version of the code
#     when this define is applied.  This is obviously a hack that should
#     be eliminated if possible.
@pytest.mark.eda
def test_lint():
    errors = 0

    # Provide this test directory's data subdirectory as a place to
    # supply mock include files for lint testing
    test_inc_dir = os.path.join(os.path.dirname(__file__),
                                'data')

    for root, dirs, files in os.walk("."): # TODO
        for filename in files:
            if (fnmatch.fnmatch(filename, '*.v')):
                fullpath = os.path.join(root, filename)
                lint_result = subprocess.run(['slang',
                                              '--lint-only',
                                              '-I',
                                              test_inc_dir,
                                              '+define+USE_SYSTEMVERILOG',
                                              fullpath])
                if (lint_result.returncode != 0):
                    print(f"Lint failed for {fullpath}")
                    errors += 1

    assert errors == 0, 'Lint failed'