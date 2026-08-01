import json


import json
import base64


def test_workflow_disable_describe_missing_alias_fails(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "disable-flow")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    dis = cli("kms", "disable-key", "--key-id", key_id)
    assert dis.returncode == 0
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["Enabled"] is False
    miss = cli("kms", "describe-key", "--key-id", "alias/does-not-exist-" + key_id[:8])
    assert miss.returncode != 0
    assert "NotFoundException" in (miss.stderr + miss.stdout)
