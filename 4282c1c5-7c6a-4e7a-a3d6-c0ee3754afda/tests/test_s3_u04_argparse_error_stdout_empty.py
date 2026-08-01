from conftest import _stderr_names_error


def test_u04_argparse_error_stdout_empty(cli, s3_client, tmp_path):
    """Argparse error: stdout MUST be empty (parse errors do not write to stdout)."""
    result = cli("s3", "cp")
    assert result.returncode in (2, 252, 255), (
        f"expected returncode in (2,252,255), got {result.returncode}"
    )
    assert result.stdout == "", (
        f"argparse error should not write to stdout, got: {result.stdout!r}"
    )
    assert _stderr_names_error(result.stderr), (
        f"stderr should signal argparse/usage error class: {result.stderr!r}"
    )
