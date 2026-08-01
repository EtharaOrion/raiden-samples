def test_get_public_key_requires_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "get-public-key missing key-id validation",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "get-public-key")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeySpec"] == "RSA_2048"
    assert metadata["KeyState"] == "Enabled"
    assert metadata["Enabled"] is True