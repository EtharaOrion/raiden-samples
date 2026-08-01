def test_encrypt_rejects_empty_key_id(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "empty-key-id validation sentinel"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]

    result = cli(
        "kms",
        "encrypt",
        "--key-id",
        "",
        "--plaintext",
        "dGVzdA==",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["KeyState"] == before["KeyState"]
    assert after["Enabled"] == before["Enabled"]