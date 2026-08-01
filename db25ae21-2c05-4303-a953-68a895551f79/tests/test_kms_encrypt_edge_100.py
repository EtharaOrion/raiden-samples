import base64
import json


def test_encrypt_rsa_oaep_roundtrip(cli, kms):
    # Seed: create an asymmetric ENCRYPT_DECRYPT KMS key compatible with RSAES_OAEP_SHA_256
    created = kms.rpc("CreateKey", {
        "KeyUsage": "ENCRYPT_DECRYPT",
        "KeySpec": "RSA_2048",
    })
    key_id = created["KeyMetadata"]["KeyId"]

    plaintext = b"secret-data-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run command under test
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--encryption-algorithm", "RSAES_OAEP_SHA_256",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Independent read: decrypt via kms and verify round trip
    dec = kms.rpc("Decrypt", {
        "CiphertextBlob": ciphertext_blob,
        "KeyId": key_id,
        "EncryptionAlgorithm": "RSAES_OAEP_SHA_256",
    })
    assert base64.b64decode(dec["Plaintext"]) == plaintext