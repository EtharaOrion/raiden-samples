def test_create_alias_empty_alias_name_rejected(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    result = cli("kms", "create-alias", "--alias-name", "", "--target-key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr or "Invalid" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert not any(a.get("TargetKeyId") == key_id for a in aliases)