import json


import json


def test_workflow_create_pool_describe(cli, cognito, tmp_path):
    r = cli("cognito-idp", "create-user-pool", "--pool-name", "wf-desc-pool")
    assert r.returncode == 0
    pid = json.loads(r.stdout)["UserPool"]["Id"]
    d = cli("cognito-idp", "describe-user-pool", "--user-pool-id", pid)
    assert d.returncode == 0
    body = json.loads(d.stdout)
    assert body["UserPool"]["Id"] == pid
    assert body["UserPool"]["Name"] == "wf-desc-pool"
