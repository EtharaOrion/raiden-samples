import json
import base64


def test_generate_data_key_aes256_roundtrip(cli, kms):
    # Seed: create a symmetric encryption KMS key
    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    # Run command under test
    result = cli("kms", "generate-data-key", "--key-id", key_id, "--key-spec", "AES_256")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert out["KeyId"].endswith(key_id) or out["KeyId"] == key_id

    # Plaintext should be 32 bytes for AES_256
    plaintext = base64.b64decode(out["Plaintext"])
    assert len(plaintext) == 32

    ciphertext_blob = out["CiphertextBlob"]
    assert ciphertext_blob

    # Independent verification: decrypting the returned CiphertextBlob
    # must yield the same plaintext data key.
    decrypt = kms.rpc("Decrypt", {"CiphertextBlob": ciphertext_blob})
    decrypted = base64.b64decode(decrypt["Plaintext"])
    assert decrypted == plaintext
    assert decrypt["KeyId"].endswith(key_id) or decrypt["KeyId"] == key_id