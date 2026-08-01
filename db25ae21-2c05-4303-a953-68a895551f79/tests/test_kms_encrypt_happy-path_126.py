import base64
import json


def test_encrypt_roundtrip_happy_path(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "encrypt-happy", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = key["KeyMetadata"]["KeyId"]

    secret = b"top-secret-value-123"
    plaintext_b64 = base64.b64encode(secret).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Independent read: decrypt the ciphertext via the backend and verify roundtrip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == secret