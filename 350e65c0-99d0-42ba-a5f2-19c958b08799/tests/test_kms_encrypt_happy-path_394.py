import json
import base64

def test_encrypt_happy_path_roundtrip(cli, kms, tmp_path):
    # Seed prerequisite state: create a symmetric ENCRYPT_DECRYPT key
    created = kms.rpc("CreateKey", {"Description": "encrypt-happy-path"})
    key_id = created["KeyMetadata"]["KeyId"]

    plaintext = b"super-secret-data-123"
    plaintext_b64 = base64.b64encode(plaintext).decode()

    # Run the command under test
    result = cli("kms", "encrypt",
                 "--key-id", key_id,
                 "--plaintext", plaintext_b64)
    assert result.returncode == 0, result.stderr

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independent read: decrypt via kms and assert round trip
    dec = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    assert base64.b64decode(dec["Plaintext"]) == plaintext
    assert dec["KeyId"].endswith(key_id) or dec["KeyId"] == key_id