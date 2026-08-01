import json
import base64

def test_generate_data_key_happy_path(cli, kms):
    create = kms.rpc("CreateKey", {"Description": "gdk-test"})
    key_id = create["KeyMetadata"]["KeyId"]

    result = cli("kms", "generate-data-key", "--key-id", key_id,
                 "--number-of-bytes", "32")
    assert result.returncode == 0

    out = json.loads(result.stdout)
    assert "CiphertextBlob" in out
    assert "Plaintext" in out
    plaintext = out["Plaintext"]
    assert len(base64.b64decode(plaintext)) == 32

    # verify the returned key id resolves to our key
    described = kms.rpc("DescribeKey", {"KeyId": out["KeyId"]})
    assert described["KeyMetadata"]["KeyId"] == key_id

    # round-trip: decrypting the ciphertext blob yields the plaintext key
    dec = kms.rpc("Decrypt", {"CiphertextBlob": out["CiphertextBlob"]})
    assert dec["Plaintext"] == plaintext