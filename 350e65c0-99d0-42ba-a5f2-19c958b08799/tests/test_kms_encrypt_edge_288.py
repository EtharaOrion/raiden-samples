import base64
import json


def test_encrypt_with_grant_tokens_roundtrip(cli, kms, tmp_path):
    # Seed a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"Description": "encrypt-grant-token-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-data-1234"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", plaintext_b64,
        "--grant-tokens", "xxxxxxxxxx",
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    ciphertext_b64 = out["CiphertextBlob"]
    assert ciphertext_b64

    # Independently verify via decrypt round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id)