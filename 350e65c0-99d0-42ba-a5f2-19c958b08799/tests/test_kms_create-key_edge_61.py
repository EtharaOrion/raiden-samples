def test_create_key_with_xks_key_id(cli, kms, tmp_path):
    xks_id = "x" * 128
    result = cli("kms", "create-key", "--xks-key-id", xks_id)
    assert result.returncode == 0, result.stderr

    import json
    out = json.loads(result.stdout)
    key_id = out["KeyMetadata"]["KeyId"]
    assert key_id

    described = kms.rpc("DescribeKey", {"KeyId": key_id})
    md = described["KeyMetadata"]
    assert md["KeyId"] == key_id
    assert md["KeyState"] in ("Enabled", "Disabled", "PendingImport", "Unavailable", "Creating")