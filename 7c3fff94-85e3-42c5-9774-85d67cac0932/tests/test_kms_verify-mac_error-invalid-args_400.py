def test_verify_mac_missing_required_mac(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"KeyUsage": "GENERATE_VERIFY_MAC", "KeySpec": "HMAC_256"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "verify-mac",
        "--message",
        "dGVzdA==",
        "--key-id",
        key_id,
        "--mac-algorithm",
        "HMAC_SHA_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "GENERATE_VERIFY_MAC"
    assert metadata["KeySpec"] == "HMAC_256"
    assert metadata["Enabled"] is True