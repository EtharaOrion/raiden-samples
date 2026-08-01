def test_list_groups_limit_edge(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-groups-limit-edge-pool"})
    pool_id = pool["UserPool"]["Id"]

    expected_names = {"edge-group-alpha", "edge-group-beta"}
    for index, group_name in enumerate(sorted(expected_names)):
        cognito.rpc(
            "CreateGroup",
            {
                "UserPoolId": pool_id,
                "GroupName": group_name,
                "Description": f"Edge group {index}",
                "Precedence": index,
            },
        )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
        "--limit",
        "60",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert {group["GroupName"] for group in output["Groups"]} == expected_names

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id, "Limit": 60})
    assert {group["GroupName"] for group in state["Groups"]} == expected_names