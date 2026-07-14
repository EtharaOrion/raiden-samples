import uuid


def test_failed_cp_to_nonexistent_bucket_no_partial_state(cli, s3_client, tmp_path):
    bystander = f"by-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bystander)
    s3_client.put_object(Bucket=bystander, Key="existing.txt", Body=b"original")

    r0 = cli("s3", "ls")
    assert r0.returncode == 0, r0.stderr
    assert bystander in r0.stdout

    src = tmp_path / "data.bin"
    src.write_bytes(b"will-fail")
    ghost = f"ghost-{uuid.uuid4().hex[:12]}"

    result = cli("s3", "cp", str(src), f"s3://{ghost}/data.bin")
    assert result.returncode != 0

    assert s3_client.get_object(Bucket=bystander, Key="existing.txt")["Body"].read() == b"original"
    keys = {
        o["Key"]
        for o in s3_client.list_objects_v2(Bucket=bystander).get("Contents", []) or []
    }
    assert keys == {"existing.txt"}
