def test_create_alias_rejects_unknown_flag(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "target for invalid create-alias test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/invalid-flag-{key_id}"

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert all(item["AliasName"] != alias_name for item in aliases_before)

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        key_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert all(item["AliasName"] != alias_name for item in aliases_after)

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id
    assert metadata["KeyState"] == "Enabled"