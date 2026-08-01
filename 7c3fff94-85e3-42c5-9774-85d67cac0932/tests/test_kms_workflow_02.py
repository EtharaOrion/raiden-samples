import json


import json
import base64


def test_workflow_asymmetric_sign_verify_and_mac(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--key-usage", "SIGN_VERIFY", "--key-spec", "RSA_2048")
    assert r.returncode == 0
    kid = json.loads(r.stdout)["KeyMetadata"]["KeyId"]

    r = cli("kms", "describe-key", "--key-id", kid)
    assert r.returncode == 0
    assert json.loads(r.stdout)["KeyMetadata"]["KeyUsage"] == "SIGN_VERIFY"

    msg = base64.b64encode(b"data-to-sign").decode()
    r = cli("kms", "sign", "--key-id", kid, "--message", msg,
            "--message-type", "RAW", "--signing-algorithm", "RSASSA_PKCS1_V1_5_SHA_256")
    assert r.returncode == 0
    sig = json.loads(r.stdout)["Signature"]

    r = cli("kms", "verify", "--key-id", kid, "--message", msg,
            "--message-type", "RAW", "--signature", sig,
            "--signing-algorithm", "RSASSA_PKCS1_V1_5_SHA_256")
    assert r.returncode == 0
    assert json.loads(r.stdout)["SignatureValid"] is True

    r = cli("kms", "get-public-key", "--key-id", kid)
    assert r.returncode == 0
    pub = json.loads(r.stdout)
    assert pub["KeyId"].endswith(kid) or kid in pub["KeyId"]
    assert "PublicKey" in pub

    # MAC key
    r = cli("kms", "create-key", "--key-usage", "GENERATE_VERIFY_MAC", "--key-spec", "HMAC_256")
    assert r.returncode == 0
    mkid = json.loads(r.stdout)["KeyMetadata"]["KeyId"]

    mmsg = base64.b64encode(b"mac-message").decode()
    r = cli("kms", "generate-mac", "--key-id", mkid, "--message", mmsg, "--mac-algorithm", "HMAC_SHA_256")
    assert r.returncode == 0
    mac = json.loads(r.stdout)["Mac"]

    r = cli("kms", "verify-mac", "--key-id", mkid, "--message", mmsg,
            "--mac", mac, "--mac-algorithm", "HMAC_SHA_256")
    assert r.returncode == 0
    assert json.loads(r.stdout)["MacValid"] is True

    # NEGATIVE: describe a non-existent alias must fail
    r = cli("kms", "describe-key", "--key-id", "alias/nonexistent-" + kid[:8])
    assert r.returncode != 0
    assert "NotFound" in (r.stderr + r.stdout)
