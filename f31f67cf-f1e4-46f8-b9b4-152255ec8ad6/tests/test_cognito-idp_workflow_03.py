import json
import uuid


def test_workflow_user_group_membership(cli, cognito, tmp_path):
    """create pool -> create group -> create user -> add to group -> list members."""
    pool_name = "wf-member-pool-" + uuid.uuid4().hex[:8]
    r = cli("cognito-idp", "create-user-pool", "--pool-name", pool_name)
    assert r.returncode == 0, r.stderr
    pool_id = json.loads(r.stdout)["UserPool"]["Id"]

    group_name = "wf-grp-" + uuid.uuid4().hex[:8]
    g = cli("cognito-idp", "create-group",
            "--group-name", group_name, "--user-pool-id", pool_id)
    assert g.returncode == 0, g.stderr

    username = "wf-user-%s@example.com" % uuid.uuid4().hex[:12]
    u = cli("cognito-idp", "admin-create-user",
            "--user-pool-id", pool_id, "--username", username,
            "--message-action", "SUPPRESS")
    assert u.returncode == 0, u.stderr
    # the service assigns the canonical username; downstream calls must use it
    uid = json.loads(u.stdout)["User"]["Username"]

    a = cli("cognito-idp", "admin-add-user-to-group",
            "--user-pool-id", pool_id, "--username", uid,
            "--group-name", group_name)
    assert a.returncode == 0, a.stderr

    m = cli("cognito-idp", "list-users-in-group",
            "--user-pool-id", pool_id, "--group-name", group_name)
    assert m.returncode == 0, m.stderr
    members = [x["Username"] for x in json.loads(m.stdout)["Users"]]
    assert uid in members
