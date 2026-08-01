def test_list_groups_happy_path(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-groups-test-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "developers",
            "Description": "Application developers",
            "Precedence": 10,
        },
    )
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "operators",
            "Description": "Application operators",
            "Precedence": 20,
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
        "developers",
        "operators",
    }

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    groups = {group["GroupName"]: group for group in state["Groups"]}
    assert set(groups) == {"developers", "operators"}
    assert groups["developers"]["Description"] == "Application developers"
    assert groups["developers"]["Precedence"] == 10
    assert groups["operators"]["Description"] == "Application operators"
    assert groups["operators"]["Precedence"] == 20