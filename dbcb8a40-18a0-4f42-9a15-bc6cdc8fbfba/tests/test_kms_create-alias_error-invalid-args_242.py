def test_create_alias_invalid_alias_name(cli, kms):
    key = kms.rpc("CreateKey", {})
    key_id = key["KeyMetadata"]["KeyId"]

    long_name = "alias/" + "x" * 300

    result = cli(
        "kms", "create-alias",
        "--alias-name", long_name,
        "--target-key-id", key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Exception" in result.stderr

    aliases = kms.rpc("ListAliases", {})["Aliases"]
    assert not any(a["AliasName"] == long_name for a in aliases)