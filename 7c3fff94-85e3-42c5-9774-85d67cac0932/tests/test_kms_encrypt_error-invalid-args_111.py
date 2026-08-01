def test_encrypt_rejects_unknown_flag_without_changing_key(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "encrypt invalid-arguments test"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["KeyState"] == "Enabled"
    assert before["Enabled"] is True

    result = cli(
        "kms",
        "encrypt",
        "--key-id",
        key_id,
        "--plaintext",
        "c2VjcmV0",
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Description"] == "encrypt invalid-arguments test"
    assert after["KeyState"] == before["KeyState"] == "Enabled"
    assert after["Enabled"] is before["Enabled"] is True