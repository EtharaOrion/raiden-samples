def test_list_groups_returns_groups_for_user_pool(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-groups-edge-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "admins",
            "Description": "Administrative users",
            "Precedence": 1,
        },
    )
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "auditors",
            "Description": "Read-only auditors",
            "Precedence": 2,
        },
    )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert {group["GroupName"] for group in output["Groups"]} == {
        "admins",
        "auditors",
    }

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    groups_by_name = {group["GroupName"]: group for group in state["Groups"]}
    assert set(groups_by_name) == {"admins", "auditors"}
    assert groups_by_name["admins"]["Description"] == "Administrative users"
    assert groups_by_name["admins"]["Precedence"] == 1
    assert groups_by_name["auditors"]["Description"] == "Read-only auditors"
    assert groups_by_name["auditors"]["Precedence"] == 2