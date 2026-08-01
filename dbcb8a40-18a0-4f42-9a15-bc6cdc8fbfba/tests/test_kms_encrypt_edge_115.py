import base64
import json


def test_encrypt_with_grant_tokens_roundtrip(cli, kms):
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
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

    decrypted = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(decrypted["Plaintext"]) == plaintext
    assert decrypted["KeyId"].endswith(key_id) or key_id in decrypted["KeyId"]