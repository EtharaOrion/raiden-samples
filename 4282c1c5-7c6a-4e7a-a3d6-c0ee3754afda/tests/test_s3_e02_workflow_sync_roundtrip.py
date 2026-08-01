import uuid


def test_workflow_sync_local_to_s3_and_back(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "src"
    src.mkdir()
    (src / "x.txt").write_bytes(b"X-content")
    (src / "y.txt").write_bytes(b"Y-content-longer")

    r1 = cli("s3", "sync", str(src), f"s3://{bucket}/")
    assert r1.returncode == 0, r1.stderr
    assert s3_client.get_object(Bucket=bucket, Key="x.txt")["Body"].read() == b"X-content"
    assert s3_client.get_object(Bucket=bucket, Key="y.txt")["Body"].read() == b"Y-content-longer"

    dst = tmp_path / "dst"
    dst.mkdir()
    r2 = cli("s3", "sync", f"s3://{bucket}/", str(dst))
    assert r2.returncode == 0, r2.stderr
    assert (dst / "x.txt").read_bytes() == b"X-content"
    assert (dst / "y.txt").read_bytes() == b"Y-content-longer"
