def test_list_groups_happy_path(cli, cognito):
    import json

    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-groups-happy-path-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

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

    assert result.returncode == 0, result.stderr
    output = json.loads(result.stdout)
    output_groups = {
        group["GroupName"]: group
        for group in output["Groups"]
    }
    assert set(output_groups) == {"developers", "operators"}
    assert output_groups["developers"]["Description"] == "Application developers"
    assert output_groups["developers"]["Precedence"] == 10
    assert output_groups["operators"]["Description"] == "Application operators"
    assert output_groups["operators"]["Precedence"] == 20

    stored = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    stored_groups = {
        group["GroupName"]: group
        for group in stored["Groups"]
    }
    assert set(stored_groups) == {"developers", "operators"}
    assert stored_groups["developers"]["UserPoolId"] == pool_id
    assert stored_groups["developers"]["Description"] == "Application developers"
    assert stored_groups["developers"]["Precedence"] == 10
    assert stored_groups["operators"]["UserPoolId"] == pool_id
    assert stored_groups["operators"]["Description"] == "Application operators"
    assert stored_groups["operators"]["Precedence"] == 20