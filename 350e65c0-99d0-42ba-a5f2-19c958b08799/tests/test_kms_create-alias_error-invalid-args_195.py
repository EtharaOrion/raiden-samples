def test_create_alias_missing_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli("kms", "create-alias", "--target-key-id", key_id)

    assert result.returncode != 0
    assert "alias-name" in result.stderr.lower() or "aliasname" in result.stderr.lower().replace("-", "")

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert all(a.get("TargetKeyId") != key_id for a in aliases)