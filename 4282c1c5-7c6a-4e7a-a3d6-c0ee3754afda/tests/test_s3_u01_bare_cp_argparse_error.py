from conftest import _stderr_names_error


def test_u01_bare_cp_argparse_error(cli, s3_client, tmp_path):
    """Bare `s3 cp` (no operands) must fail with argparse-style error.

    Floor-tightened: stderr must contain a positive substring proving it is an
    argparse error (not a Python "can't open file" error from an empty stub).
    """
    result = cli("s3", "cp")
    assert result.returncode in (2, 252, 255), (
        f"expected returncode in (2,252,255), got {result.returncode}; stderr={result.stderr!r}"
    )
    assert _stderr_names_error(result.stderr), (
        f"stderr should signal argparse/usage error class: {result.stderr!r}"
    )
