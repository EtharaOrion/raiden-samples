def test_create_alias_happy_path(cli, kms, tmp_path):
    create = kms.rpc("CreateKey", {"Description": "alias-target"})
    key_id = create["KeyMetadata"]["KeyId"]

    alias_name = "alias/test-happy-alias-v23"

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