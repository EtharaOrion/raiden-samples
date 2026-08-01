def test_encrypt_invalid_key_id_not_found(cli, kms, tmp_path):
    bogus_key_id = "x" * 300
    plaintext = b"secret-data"
    pt_file = tmp_path / "pt.bin"
    pt_file.write_bytes(plaintext)

    result = cli(
        "kms", "encrypt",
        "--key-id", bogus_key_id,
        "--plaintext", "fileb://" + str(pt_file),
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    stderr = result.stderr
    assert (
        "NotFoundException" in stderr
        or "NotFound" in stderr
        or "ValidationException" in stderr
        or "InvalidKeyId" in stderr
        or "Invalid" in stderr
    )

    # Confirm no key with this bogus id exists in state
    listed = kms.rpc("ListKeys", {})
    for k in listed.get("Keys", []):
        assert k.get("KeyId") != bogus_key_id