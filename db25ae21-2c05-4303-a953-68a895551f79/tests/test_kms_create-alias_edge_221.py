def test_create_alias_long_name_succeeds(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]

    alias_name = "alias/" + ("a" * 240)

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", key_id,
    )
    assert result.returncode == 0

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id

    described = kms.rpc("DescribeKey", {"KeyId": alias_name})["KeyMetadata"]
    assert described["KeyId"] == key_id