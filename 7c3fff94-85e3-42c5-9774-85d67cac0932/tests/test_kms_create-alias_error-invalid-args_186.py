def test_create_alias_missing_target_key_id(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {"Description": "create-alias missing target test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/missing-target-{key_id}"

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert all(item["AliasName"] != alias_name for item in aliases_before)

    result = cli("kms", "create-alias", "--alias-name", alias_name)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--target-key-id" in result.stderr

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert all(item["AliasName"] != alias_name for item in aliases_after)

    metadata = kms.rpc("DescribeKey", {"KeyId": key_id})["KeyMetadata"]
    assert metadata["KeyId"] == key_id