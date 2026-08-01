def test_get_group_existing_edge_group(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "get-group-edge-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "x",
            "Description": "edge group",
            "Precedence": 0,
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        "x",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert output["Group"]["GroupName"] == "x"
    assert output["Group"]["UserPoolId"] == pool_id
    assert output["Group"]["Description"] == "edge group"
    assert output["Group"]["Precedence"] == 0

    stored = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": "x"},
    )["Group"]
    assert stored["GroupName"] == "x"
    assert stored["UserPoolId"] == pool_id
    assert stored["Description"] == "edge group"
    assert stored["Precedence"] == 0