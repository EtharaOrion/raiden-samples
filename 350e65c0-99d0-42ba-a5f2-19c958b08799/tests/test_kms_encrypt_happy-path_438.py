import base64
import json


def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    # Seed prerequisite state: create a symmetric ENCRYPT_DECRYPT key.
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-value-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test.
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Independent read: decrypt the produced ciphertext via the raw client and
    # assert the round trip recovers the original plaintext.
    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or decrypted["KeyId"] == key_id