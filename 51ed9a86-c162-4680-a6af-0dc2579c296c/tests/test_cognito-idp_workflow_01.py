import json


import json


def test_workflow_create_pool_list_user_pools(cli, cognito, tmp_path):
    r = cli("cognito-idp", "create-user-pool", "--pool-name", "wf-list-pool")
    assert r.returncode == 0
    pid = json.loads(r.stdout)["UserPool"]["Id"]
    l = cli("cognito-idp", "list-user-pools", "--max-results", "60")
    assert l.returncode == 0
    pools = json.loads(l.stdout)["UserPools"]
    assert pid in [p["Id"] for p in pools]
