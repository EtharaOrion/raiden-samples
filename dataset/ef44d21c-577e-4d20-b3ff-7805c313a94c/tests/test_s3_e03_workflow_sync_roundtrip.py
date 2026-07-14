import os
import uuid


def test_workflow_sync_local_to_s3_to_local_roundtrip(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=bucket)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    a = b"roundtrip-alpha"
    b = os.urandom(2048)
    (src_dir / "alpha.txt").write_bytes(a)
    (src_dir / "beta.bin").write_bytes(b)

    r1 = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r1.returncode == 0, r1.stderr
    assert s3_client.get_object(Bucket=bucket, Key="alpha.txt")["Body"].read() == a
    assert s3_client.get_object(Bucket=bucket, Key="beta.bin")["Body"].read() == b

    dest_dir = tmp_path / "dest"
    r2 = cli("s3", "sync", f"s3://{bucket}/", str(dest_dir))
    assert r2.returncode == 0, r2.stderr
    assert (dest_dir / "alpha.txt").read_bytes() == a
    assert (dest_dir / "beta.bin").read_bytes() == b
