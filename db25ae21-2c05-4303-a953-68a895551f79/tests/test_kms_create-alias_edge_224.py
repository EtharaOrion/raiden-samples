def test_create_alias_creates_alias_for_key(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    alias_name = "alias/test-create-alias-happy"

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    matching = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0].get("TargetKeyId") == key_id

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})
    assert described["KeyMetadata"]["KeyId"] == key_id