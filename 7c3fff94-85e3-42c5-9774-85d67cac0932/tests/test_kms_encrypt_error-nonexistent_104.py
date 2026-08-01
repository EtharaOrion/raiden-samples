def test_encrypt_nonexistent_key_returns_not_found(cli, kms, tmp_path):
    import uuid

    marker = f"encrypt-nonexistent-{uuid.uuid4()}"
    created = kms.rpc("CreateKey", {"Description": marker})
    existing_key_id = created["KeyMetadata"]["KeyId"]

    plaintext_file = tmp_path / "plaintext.bin"
    plaintext_file.write_bytes(b"secret plaintext")

    nonexistent_key_id = str(uuid.uuid4())
    assert nonexistent_key_id != existing_key_id

    result = cli(
        "kms",
        "encrypt",
        "--key-id",
        nonexistent_key_id,
        "--plaintext",
        f"fileb://{plaintext_file}",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "NotFoundException" in result.stderr

    metadata = kms.rpc("DescribeKey", {"KeyId": existing_key_id})["KeyMetadata"]
    assert metadata["KeyId"] == existing_key_id
    assert metadata["Description"] == marker
    assert metadata["Enabled"] is True
    assert metadata["KeyState"] == "Enabled"