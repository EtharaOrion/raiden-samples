import uuid

from _s3_http import S3HTTPError as ClientError


def test_workflow_mb_cp_ls_sync_mv_full_roundtrip(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0, r.stderr
    names = {b["Name"] for b in s3_client.list_buckets().get("Buckets", []) or []}
    assert bucket in names

    src = tmp_path / "f.bin"
    payload = b"5cmd-workflow-payload-bytes"
    src.write_bytes(payload)
    r = cli("s3", "cp", str(src), f"s3://{bucket}/f.bin")
    assert r.returncode == 0, r.stderr
    assert s3_client.get_object(Bucket=bucket, Key="f.bin")["Body"].read() == payload

    r = cli("s3", "ls", f"s3://{bucket}/")
    assert r.returncode == 0, r.stderr
    assert "f.bin" in r.stdout

    dl_dir = tmp_path / "dl"
    dl_dir.mkdir()
    r = cli("s3", "sync", f"s3://{bucket}/", str(dl_dir))
    assert r.returncode == 0, r.stderr
    assert (dl_dir / "f.bin").read_bytes() == payload

    r = cli("s3", "mv", f"s3://{bucket}/f.bin", f"s3://{bucket}/moved.bin")
    assert r.returncode == 0, r.stderr
    assert s3_client.get_object(Bucket=bucket, Key="moved.bin")["Body"].read() == payload
    try:
        s3_client.head_object(Bucket=bucket, Key="f.bin")
        raise AssertionError("source key should be removed after mv")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")
