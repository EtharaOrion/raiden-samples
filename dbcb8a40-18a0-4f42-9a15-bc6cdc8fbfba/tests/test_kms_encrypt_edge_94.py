import base64
import json


def test_encrypt_symmetric_default_roundtrip(cli, kms):
    key = kms.rpc("CreateKey", {"Description": "encrypt-edge", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = key["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-data-42"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--encryption-algorithm", "SYMMETRIC_DEFAULT",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Independently decrypt via the raw kms client and verify round trip.
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id