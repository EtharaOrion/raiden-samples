def test_delete_alias_rejects_unknown_attribute_definitions(cli, kms, tmp_path):
    key = kms.rpc("CreateKey", {"Description": "delete-alias invalid-args test"})
    key_id = key["KeyMetadata"]["KeyId"]
    suffix = "".join(
        char if char.isalnum() or char in "_-" else "-"
        for char in tmp_path.name
    )
    alias_name = f"alias/delete-invalid-{suffix}"

    kms.rpc("CreateAlias", {"AliasName": alias_name, "TargetKeyId": key_id})

    result = cli(
        "kms",
        "delete-alias",
        "--alias-name",
        alias_name,
        "--attribute-definitions",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    matching = [alias_ for alias_ in aliases if alias_["AliasName"] == alias_name]
    assert len(matching) == 1
    assert matching[0]["TargetKeyId"] == key_id