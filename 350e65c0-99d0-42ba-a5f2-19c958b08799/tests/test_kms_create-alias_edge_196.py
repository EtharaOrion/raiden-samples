def test_create_alias_creates_alias(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {})["KeyMetadata"]
    key_id = key["KeyId"]
    alias_name = "alias/happy-path-alias-xyz"

    # ensure alias not present beforehand
    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert alias_name not in [a["AliasName"] for a in aliases_before]

    result = cli("kms", "create-alias",
                 "--alias-name", alias_name,
                 "--target-key-id", key_id)
    assert result.returncode == 0

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    match = [a for a in aliases_after if a["AliasName"] == alias_name]
    assert len(match) == 1
    assert match[0].get("TargetKeyId") == key_id