import uuid


def test_failed_cp_to_nonexistent_bucket_preserves_other_state(cli, s3_client, tmp_path):
    real_bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=real_bucket)

    seed = tmp_path / "seed.bin"
    seed.write_bytes(b"seed-bytes")
    r_seed = cli("s3", "cp", str(seed), f"s3://{real_bucket}/seed.bin")
    assert r_seed.returncode == 0, r_seed.stderr
    assert s3_client.get_object(Bucket=real_bucket, Key="seed.bin")["Body"].read() == b"seed-bytes"

    missing_bucket = f"missing-{uuid.uuid4().hex[:12]}"
    bad = tmp_path / "bad.bin"
    bad.write_bytes(b"bad-payload")
    result = cli("s3", "cp", str(bad), f"s3://{missing_bucket}/k.bin")
    assert result.returncode != 0

    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=real_bucket).get("Contents", []) or []}
    assert keys == {"seed.bin"}
    assert s3_client.get_object(Bucket=real_bucket, Key="seed.bin")["Body"].read() == b"seed-bytes"
