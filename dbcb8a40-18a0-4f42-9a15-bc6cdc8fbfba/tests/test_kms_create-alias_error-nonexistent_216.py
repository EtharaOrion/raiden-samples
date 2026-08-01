def test_create_alias_error_nonexistent(cli, kms, tmp_path):
    import uuid
    missing_key_id = str(uuid.uuid4())
    alias_name = "alias/test-nonexistent-" + uuid.uuid4().hex

    result = cli(
        "kms", "create-alias",
        "--alias-name", alias_name,
        "--target-key-id", missing_key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFound" in result.stderr

    aliases = kms.rpc("ListAliases", {}).get("Aliases", [])
    assert all(a.get("AliasName") != alias_name for a in aliases)