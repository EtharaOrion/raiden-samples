def test_create_alias_missing_alias_name(cli, kms):
    created = kms.rpc("CreateKey", {})
    key_id = created["KeyMetadata"]["KeyId"]

    result = cli("kms", "create-alias", "--target-key-id", key_id)
    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "alias-name" in result.stderr.lower() or "aliasname" in result.stderr.lower()

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    for a in aliases:
        assert a.get("TargetKeyId") != key_id