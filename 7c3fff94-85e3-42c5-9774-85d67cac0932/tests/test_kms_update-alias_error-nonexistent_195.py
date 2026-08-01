def test_update_alias_nonexistent_alias(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "target for nonexistent alias test"})
    key_id = key["KeyMetadata"]["KeyId"]
    missing_alias = f"alias/nonexistent-update-{key_id}"

    result = cli(
        "kms",
        "update-alias",
        "--alias-name",
        missing_alias,
        "--target-key-id",
        key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert all(alias["AliasName"] != missing_alias for alias in aliases)