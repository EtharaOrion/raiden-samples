import uuid

import time

def test_sync02_modified_file_reuploaded(cli, s3_client, tmp_path):
    """Sync, modify a file, sync again -> S3 reflects modified bytes."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    (tmp_path / "a.txt").write_bytes(b"v1")
    r1 = cli("s3", "sync", str(tmp_path), f"s3://{bucket}/p")
    assert r1.returncode == 0, r1.stderr
    body1 = s3_client.get_object(Bucket=bucket, Key="p/a.txt")["Body"].read()
    assert body1 == b"v1"
    time.sleep(1)
    (tmp_path / "a.txt").write_bytes(b"version-two-longer")
    r2 = cli("s3", "sync", str(tmp_path), f"s3://{bucket}/p")
    assert r2.returncode == 0, r2.stderr
    body2 = s3_client.get_object(Bucket=bucket, Key="p/a.txt")["Body"].read()
    assert body2 == b"version-two-longer", f"got {body2!r}"
