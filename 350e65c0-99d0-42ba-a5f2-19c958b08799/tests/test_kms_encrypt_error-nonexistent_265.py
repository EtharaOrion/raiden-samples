import base64

def test_encrypt_nonexistent_key(cli, kms):
    missing_key_id = "00000000-1111-2222-3333-444444444444"

    # Ensure the key really does not exist
    found = False
    try:
        resp = kms.rpc("DescribeKey", {"KeyId": missing_key_id})
        if resp.get("KeyMetadata"):
            found = True
    except Exception:
        found = False
    assert not found, "precondition failed: key unexpectedly exists"

    plaintext = base64.b64encode(b"secret data").decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", missing_key_id,
        "--plaintext", plaintext,
    )

    assert result.returncode != 0
    assert "NotFoundException" in result.stderr