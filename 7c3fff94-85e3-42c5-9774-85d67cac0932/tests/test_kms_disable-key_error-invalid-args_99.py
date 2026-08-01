def test_disable_key_rejects_unknown_attribute_definitions(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid-args-disable-key-test"})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "disable-key",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"