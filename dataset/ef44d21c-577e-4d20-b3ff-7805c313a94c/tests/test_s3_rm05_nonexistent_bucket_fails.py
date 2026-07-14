

def test_rm05_nonexistent_bucket_fails_with_clear_error(cli, s3_client, tmp_path):
    """rm against a nonexistent bucket -> nonzero exit and clear stderr."""
    r = cli("s3", "rm", "s3://nonexistent-bucket-xyz-rm05/key")
    assert r.returncode != 0, f"expected nonzero, got 0; stdout={r.stdout!r}"
    stderr_lower = r.stderr.lower()
    assert (
        "nosuchbucket" in stderr_lower
        or "does not exist" in stderr_lower
        or "not found" in stderr_lower
        or "bucket" in stderr_lower
    ), f"stderr should reference the missing bucket: {r.stderr!r}"
    assert "Traceback (most recent call last)" not in r.stderr
