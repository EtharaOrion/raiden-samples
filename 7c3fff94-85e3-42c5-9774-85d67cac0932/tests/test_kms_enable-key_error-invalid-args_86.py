def test_enable_key_rejects_unknown_attribute_definitions(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "enable-key invalid arguments test"})
    key_id = created["KeyMetadata"]["KeyId"]

    kms.rpc("DisableKey", {"KeyId": key_id})
    before = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert before["Enabled"] is False
    assert before["KeyState"] == "Disabled"

    result = cli(
        "kms",
        "enable-key",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    after = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert after["KeyId"] == key_id
    assert after["Enabled"] is False
    assert after["KeyState"] == "Disabled"