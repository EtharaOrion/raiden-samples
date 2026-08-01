def test_create_alias_missing_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "target for missing alias name test"})
    key_id = key["KeyMetadata"]["KeyId"]

    aliases_before = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias.get("TargetKeyId") != key_id for alias in aliases_before)

    result = cli("kms", "create-alias", "--target-key-id", key_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    aliases_after = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias.get("TargetKeyId") != key_id for alias in aliases_after)