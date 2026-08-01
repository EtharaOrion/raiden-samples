import base64
import json


def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    # Seed prerequisite: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-value-123"
    b64_plaintext = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli(
        "kms", "encrypt",
        "--key-id", key_id,
        "--plaintext", b64_plaintext,
    )
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Assert effect via independent read: decrypt the produced ciphertext
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    recovered = base64.b64decode(decrypt["Plaintext"])
    assert recovered == plaintext
    assert decrypt["KeyId"].endswith(key_id) or key_id in decrypt["KeyId"]