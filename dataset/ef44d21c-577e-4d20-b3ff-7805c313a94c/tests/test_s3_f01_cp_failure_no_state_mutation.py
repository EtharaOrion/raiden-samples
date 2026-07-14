import uuid


def test_failed_cp_to_nonexistent_bucket_preserves_bystander(cli, s3_client, tmp_path):
    bystander = f"by-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bystander)

    src_keep = tmp_path / "existing.txt"
    src_keep.write_bytes(b"original")
    r_cp = cli("s3", "cp", str(src_keep), f"s3://{bystander}/existing.txt")
    assert r_cp.returncode == 0, r_cp.stderr
    assert s3_client.get_object(Bucket=bystander, Key="existing.txt")["Body"].read() == b"original"

    src = tmp_path / "data.bin"
    src.write_bytes(b"will-fail")
    ghost = f"ghost-{uuid.uuid4().hex[:12]}"
    result = cli("s3", "cp", str(src), f"s3://{ghost}/data.bin")
    assert result.returncode != 0

    assert s3_client.get_object(Bucket=bystander, Key="existing.txt")["Body"].read() == b"original"
