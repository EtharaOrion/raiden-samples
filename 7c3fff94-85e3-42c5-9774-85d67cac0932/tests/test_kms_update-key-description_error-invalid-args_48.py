def test_update_key_description_rejects_empty_key_id(cli, kms):
    created = kms.rpc(
        "CreateKey",
        {"Description": "original description"},
    )
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli(
        "kms",
        "update-key-description",
        "--key-id",
        "",
        "--description",
        "<string>",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid length" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["Description"] == "original description"