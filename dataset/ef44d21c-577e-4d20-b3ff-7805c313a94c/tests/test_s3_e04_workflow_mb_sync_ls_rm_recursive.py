import uuid


def test_workflow_mb_then_sync_then_ls_then_rm_recursive(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"

    r_mb = cli("s3", "mb", f"s3://{bucket}")
    assert r_mb.returncode == 0, r_mb.stderr

    src_dir = tmp_path / "payload"
    src_dir.mkdir()
    (src_dir / "f1.txt").write_bytes(b"one")
    (src_dir / "f2.txt").write_bytes(b"twotwo")

    r_sync = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r_sync.returncode == 0, r_sync.stderr
    assert s3_client.get_object(Bucket=bucket, Key="f1.txt")["Body"].read() == b"one"
    assert s3_client.get_object(Bucket=bucket, Key="f2.txt")["Body"].read() == b"twotwo"

    r_ls = cli("s3", "ls", f"s3://{bucket}/")
    assert r_ls.returncode == 0, r_ls.stderr
    assert "f1.txt" in r_ls.stdout
    assert "f2.txt" in r_ls.stdout

    r_rm = cli("s3", "rm", f"s3://{bucket}/", "--recursive")
    assert r_rm.returncode == 0, r_rm.stderr

    remaining = s3_client.list_objects_v2(Bucket=bucket).get("Contents", []) or []
    assert remaining == []
