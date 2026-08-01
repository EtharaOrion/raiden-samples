def test_generate_data_key_missing_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "generate-data-key invalid-args sentinel"},
    )
    key_metadata = created["KeyMetadata"]
    key_id = key_metadata["KeyId"]

    result = cli("kms", "generate-data-key")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--key-id" in result.stderr

    described = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert described["KeyId"] == key_id
    assert described["Description"] == "generate-data-key invalid-args sentinel"
    assert described["Enabled"] is True