def test_delete_alias_rejects_empty_alias_name(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {"Description": "delete-alias invalid-args test"})
    key_id = key["KeyMetadata"]["KeyId"]
    alias_name = f"alias/delete-alias-empty-{tmp_path.name}"

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli("kms", "delete-alias", "--alias-name", "")

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Parameter validation failed" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert any(
        alias.get("AliasName") == alias_name
        and alias.get("TargetKeyId") == key_id
        for alias in aliases
    )