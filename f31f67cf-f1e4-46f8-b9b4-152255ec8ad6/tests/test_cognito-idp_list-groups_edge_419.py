def test_list_groups_returns_existing_groups(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-groups-edge-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "edge-group",
            "Description": "Group used to verify list-groups",
            "Precedence": 7,
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
    groups = output["Groups"]
    assert any(
        group["GroupName"] == "edge-group"
        and group["UserPoolId"] == pool_id
        and group["Description"] == "Group used to verify list-groups"
        and group["Precedence"] == 7
        for group in groups
    )

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    assert any(
        group["GroupName"] == "edge-group"
        and group["UserPoolId"] == pool_id
        for group in state["Groups"]
    )