def test_get_group_existing_group_edge(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "get-group-edge-pool"})["UserPool"]
    pool_id = pool["Id"]
    group_name = "edge-group_01"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Edge case group",
            "Precedence": 0,
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        group_name,
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == group_name
    assert output["Group"]["UserPoolId"] == pool_id
    assert output["Group"]["Description"] == "Edge case group"
    assert output["Group"]["Precedence"] == 0

    stored_group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert stored_group["GroupName"] == group_name
    assert stored_group["UserPoolId"] == pool_id
    assert stored_group["Description"] == "Edge case group"
    assert stored_group["Precedence"] == 0