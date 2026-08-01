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
    output_groups = {group["GroupName"]: group for group in output["Groups"]}
    assert set(output_groups) == {"developers", "operators"}
    assert output_groups["developers"]["Description"] == "Application developers"
    assert output_groups["developers"]["Precedence"] == 10
    assert output_groups["operators"]["Description"] == "Application operators"
    assert output_groups["operators"]["Precedence"] == 20

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    state_groups = {group["GroupName"]: group for group in state["Groups"]}
    assert set(state_groups) == {"developers", "operators"}
    assert all(group["UserPoolId"] == pool_id for group in state_groups.values())