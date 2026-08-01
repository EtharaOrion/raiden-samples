def test_create_alias_nonexistent_target(cli, kms):
    import uuid

    alias_name = f"alias/nonexistent-target-{uuid.uuid4().hex}"
    target_key_id = str(uuid.uuid4())

    keys = []
    marker = None
    while True:
        payload = {"Marker": marker} if marker else {}
        page = kms.rpc("ListKeys", payload)
        keys.extend(page.get("Keys", []))
        if not page.get("Truncated"):
            break
        marker = page["NextMarker"]

    assert all(key["KeyId"] != target_key_id for key in keys)

    aliases_before = []
    marker = None
    while True:
        payload = {"Marker": marker} if marker else {}
        page = kms.rpc("ListAliases", payload)
        aliases_before.extend(page.get("Aliases", []))
        if not page.get("Truncated"):
            break
        marker = page["NextMarker"]

    assert all(alias["AliasName"] != alias_name for alias in aliases_before)

    result = cli(
        "kms",
        "create-alias",
        "--alias-name",
        alias_name,
        "--target-key-id",
        target_key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    aliases_after = []
    marker = None
    while True:
        payload = {"Marker": marker} if marker else {}
        page = kms.rpc("ListAliases", payload)
        aliases_after.extend(page.get("Aliases", []))
        if not page.get("Truncated"):
            break
        marker = page["NextMarker"]

    assert all(alias["AliasName"] != alias_name for alias in aliases_after)