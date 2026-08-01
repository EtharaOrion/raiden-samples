def test_sign_missing_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "sign missing key-id validation",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]

    result = cli(
        "kms",
        "sign",
        "--message",
        "dGVzdA==",
        "--signing-algorithm",
        "RSASSA_PKCS1_V1_5_SHA_256",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == before["KeyId"]
    assert after["Description"] == "sign missing key-id validation"
    assert after["Enabled"] is True
    assert after["KeyState"] == before["KeyState"] == "Enabled"