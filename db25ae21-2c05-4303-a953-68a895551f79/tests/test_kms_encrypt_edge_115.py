import base64
import json


def test_encrypt_with_grant_tokens_roundtrip(cli, kms, tmp_path):
    # Seed: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"sensitive-info-1234"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test: encrypt with a grant token
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

    # Independent read: decrypt the ciphertext and assert round-trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_b64})
    assert base64.b64decode(dec["Plaintext"]) == plaintext

    # The decrypt resolves to the same key we encrypted with
    described = kms.rpc("DescribeKey", {"KeyId": dec["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id