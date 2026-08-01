def test_get_public_key_rejects_unknown_flag(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {
            "Description": "asymmetric key for invalid argument test",
            "KeyUsage": "SIGN_VERIFY",
            "KeySpec": "RSA_2048",
        },
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "get-public-key",
        "--key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyUsage"] == "SIGN_VERIFY"
    assert metadata["KeySpec"] == "RSA_2048"
    assert metadata["Enabled"] is True