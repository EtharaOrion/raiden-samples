import uuid


def test_workflow_cp_then_rm_then_ls_omits_key(cli, s3_client, tmp_path):
    bucket = f"wf-{uuid.uuid4().hex[:10]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "payload.bin"
    payload = b"ephemeral"
    src.write_bytes(payload)

    r_cp = cli("s3", "cp", str(src), f"s3://{bucket}/payload.bin")
    assert r_cp.returncode == 0, r_cp.stderr
    assert s3_client.get_object(Bucket=bucket, Key="payload.bin")["Body"].read() == payload

    r_rm = cli("s3", "rm", f"s3://{bucket}/payload.bin")
    assert r_rm.returncode == 0, r_rm.stderr

    r_ls = cli("s3", "ls", f"s3://{bucket}/")
    assert "payload.bin" not in r_ls.stdout

    listing = s3_client.list_objects_v2(Bucket=bucket).get("Contents", []) or []
    assert listing == []
