import uuid

from _s3_http import S3HTTPError as ClientError


def test_workflow_mb_cp_ls_rm_full_lifecycle(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"

    r_mb = cli("s3", "mb", f"s3://{bucket}")
    assert r_mb.returncode == 0, r_mb.stderr

    src = tmp_path / "first.bin"
    payload = b"workflow-first"
    src.write_bytes(payload)
    r_cp = cli("s3", "cp", str(src), f"s3://{bucket}/first.bin")
    assert r_cp.returncode == 0, r_cp.stderr
    assert s3_client.get_object(Bucket=bucket, Key="first.bin")["Body"].read() == payload

    r_ls = cli("s3", "ls", f"s3://{bucket}/")
    assert r_ls.returncode == 0, r_ls.stderr
    assert "first.bin" in r_ls.stdout

    r_rm = cli("s3", "rm", f"s3://{bucket}/first.bin")
    assert r_rm.returncode == 0, r_rm.stderr

    try:
        s3_client.head_object(Bucket=bucket, Key="first.bin")
        raise AssertionError("object should be removed at end of workflow")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")
