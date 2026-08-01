import base64
import json


def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    # Seed prerequisite: create a symmetric ENCRYPT_DECRYPT key
    create = kms.rpc("CreateKey", {"Description": "encrypt-test", "KeyUsage": "ENCRYPT_DECRYPT"})
    key_id = create["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-data-1234"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli("kms", "encrypt", "--key-id", key_id, "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]

    # Independent read: decrypt the ciphertext via kms and assert round-trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    recovered = base64.b64decode(dec["Plaintext"])
    assert recovered == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id