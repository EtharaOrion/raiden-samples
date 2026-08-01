def test_describe_key_nonexistent_returns_not_found(cli, kms):
    import uuid

    created = kms.rpc(
        "CreateKey",
        {"Description": "describe-key nonexistent error test prerequisite"},
    )
    existing_key_id = created["KeyMetadata"]["KeyId"]

    nonexistent_key_id = str(uuid.uuid4())
    while nonexistent_key_id == existing_key_id:
        nonexistent_key_id = str(uuid.uuid4())

    result = cli(
        "kms",
        "describe-key",
        "--key-id",
        nonexistent_key_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": existing_key_id})["KeyMetadata"]
    assert metadata["KeyId"] == existing_key_id
    assert metadata["KeyState"] == "Enabled"
    assert metadata["Enabled"] is True