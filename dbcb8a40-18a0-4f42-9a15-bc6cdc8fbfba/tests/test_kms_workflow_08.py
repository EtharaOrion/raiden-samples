import json


import json
import base64


def test_workflow_schedule_deletion_describe(cli, kms, tmp_path):
    r = cli("kms", "create-key", "--description", "to-delete")
    assert r.returncode == 0
    key_id = json.loads(r.stdout)["KeyMetadata"]["KeyId"]
    s = cli("kms", "schedule-key-deletion", "--key-id", key_id, "--pending-window-in-days", "7")
    assert s.returncode == 0
    d = cli("kms", "describe-key", "--key-id", key_id)
    assert d.returncode == 0
    assert json.loads(d.stdout)["KeyMetadata"]["KeyState"] == "PendingDeletion"
