def test_delete_alias_missing_required_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "delete-alias missing argument test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = "alias/delete-alias-missing-" + key_id

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "delete-alias")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--alias-name" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias["AliasName"] == alias_name and alias.get("TargetKeyId") == key_id
        for alias in aliases
    )