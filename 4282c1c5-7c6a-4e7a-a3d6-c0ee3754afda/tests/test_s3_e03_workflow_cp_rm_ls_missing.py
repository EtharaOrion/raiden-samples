import uuid

from _s3_http import S3HTTPError as ClientError


def test_workflow_cp_then_rm_then_object_gone(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "u.bin"
    src.write_bytes(b"upload-then-remove")
    r_cp = cli("s3", "cp", str(src), f"s3://{bucket}/u.bin")
    assert r_cp.returncode == 0, r_cp.stderr

    r_ls = cli("s3", "ls", f"s3://{bucket}/")
    assert r_ls.returncode == 0, r_ls.stderr
    assert "u.bin" in r_ls.stdout

    r_rm = cli("s3", "rm", f"s3://{bucket}/u.bin")
    assert r_rm.returncode == 0, r_rm.stderr

    try:
        s3_client.head_object(Bucket=bucket, Key="u.bin")
        raise AssertionError("u.bin should be removed")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")
