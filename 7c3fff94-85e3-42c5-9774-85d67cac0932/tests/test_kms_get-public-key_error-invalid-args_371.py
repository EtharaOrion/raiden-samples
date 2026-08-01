def test_get_public_key_rejects_empty_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for empty key-id validation",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "Enabled"

    result = cli("kms", "get-public-key", "--key-id", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == before["KeyState"]
    assert after["Enabled"] is True
    assert after["KeyUsage"] == "SIGN_VERIFY"
    assert after["KeySpec"] == "RSA_2048"