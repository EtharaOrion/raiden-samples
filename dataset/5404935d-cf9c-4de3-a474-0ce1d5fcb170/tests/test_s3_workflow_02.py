

def test_workflow_cp_roundtrip_and_recursive_rm(cli, s3_client, tmp_path):
    import uuid
    from _s3_http import S3HTTPError as ClientError

    bucket = f"test-rt-rm-{uuid.uuid4().hex[:12]}"
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    blobs = {
        "prefix/one.bin": bytes(range(256)),
        "prefix/two.bin": b"\xff" * 1024,
        "other/keep.txt": b"keep me",
    }
    for key, data in blobs.items():
        local = tmp_path / key.replace("/", "_")
        local.write_bytes(data)
        r = cli("s3", "cp", str(local), f"s3://{bucket}/{key}")
        assert r.returncode == 0

    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert set(blobs).issubset(keys)

    rt = tmp_path / "rt.bin"
    r = cli("s3", "cp", f"s3://{bucket}/prefix/one.bin", str(rt))
    assert r.returncode == 0
    assert rt.read_bytes() == blobs["prefix/one.bin"]

    r = cli("s3", "rm", f"s3://{bucket}/prefix", "--recursive")
    assert r.returncode == 0

    remaining = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "other/keep.txt" in remaining
    assert not any(k.startswith("prefix/") for k in remaining)

    for gone in ("prefix/one.bin", "prefix/two.bin"):
        try:
            s3_client.head_object(Bucket=bucket, Key=gone)
            raise AssertionError(f"{gone} should be deleted")
        except ClientError as e:
            assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    r = cli("s3", "rm", f"s3://{bucket}/prefix/one.bin")
    assert r.returncode == 0

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
