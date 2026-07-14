import uuid


def test_workflow_mb_then_cp_then_ls_reflects_state(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0, r.stderr
    names = {b["Name"] for b in s3_client.list_buckets().get("Buckets", []) or []}
    assert bucket in names

    src = tmp_path / "obj.bin"
    payload = b"mb-cp-ls-workflow"
    src.write_bytes(payload)

    r = cli("s3", "cp", str(src), f"s3://{bucket}/obj.bin")
    assert r.returncode == 0, r.stderr
    assert s3_client.get_object(Bucket=bucket, Key="obj.bin")["Body"].read() == payload

    r = cli("s3", "ls", f"s3://{bucket}/")
    assert r.returncode == 0, r.stderr
    assert "obj.bin" in r.stdout
