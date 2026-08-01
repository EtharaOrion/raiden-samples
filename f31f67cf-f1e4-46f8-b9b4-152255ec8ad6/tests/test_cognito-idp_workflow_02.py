import json


def test_workflow_pool_group_lifecycle(cli, cognito, tmp_path):
    """create-user-pool -> create-group -> get-group -> list-groups, all via CLI."""
    r = cli("cognito-idp", "create-user-pool", "--pool-name", "wf-group-pool")
    assert r.returncode == 0, r.stderr
    pool_id = json.loads(r.stdout)["UserPool"]["Id"]

    group_name = "wf-group-a"
    g = cli("cognito-idp", "create-group",
            "--group-name", group_name, "--user-pool-id", pool_id)
    assert g.returncode == 0, g.stderr

    got = cli("cognito-idp", "get-group",
              "--group-name", group_name, "--user-pool-id", pool_id)
    assert got.returncode == 0, got.stderr
    assert json.loads(got.stdout)["Group"]["GroupName"] == group_name

    lst = cli("cognito-idp", "list-groups", "--user-pool-id", pool_id)
    assert lst.returncode == 0, lst.stderr
    names = [x["GroupName"] for x in json.loads(lst.stdout)["Groups"]]
    assert group_name in names
