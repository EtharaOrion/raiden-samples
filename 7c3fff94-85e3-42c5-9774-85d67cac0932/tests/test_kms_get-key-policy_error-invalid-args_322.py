def test_get_key_policy_rejects_invalid_attribute_definitions(cli, kms):
    created = kms.rpc("CreateKey", {"Description": "invalid get-key-policy arguments"})
    key_id = created["KeyMetadata"]["KeyId"]

    before = kms.rpc("GetKeyPolicy", {
        "KeyId": key_id,
        "PolicyName": "default",
    })

    result = cli(
        "kms",
        "get-key-policy",
        "--key-id",
        key_id,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "unknown option" in result.stderr.lower()

    after = kms.rpc("GetKeyPolicy", {
        "KeyId": key_id,
        "PolicyName": "default",
    })
    assert after["Policy"] == before["Policy"]

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "Enabled"