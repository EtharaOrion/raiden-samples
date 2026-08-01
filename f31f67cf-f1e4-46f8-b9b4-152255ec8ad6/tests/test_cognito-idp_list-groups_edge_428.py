def test_list_groups_accepts_next_token(cli, cognito):
    import json

    pool = cognito.rpc("CreateUserPool", {"PoolName": "list-groups-token-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "token-test-group",
            "Description": "group for next-token listing",
        },
    )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
        "--next-token",
        "x",
    )

    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert isinstance(output.get("Groups"), list)

    state = cognito.rpc("ListGroups", {"UserPoolId": pool_id})
    groups = {group["GroupName"]: group for group in state["Groups"]}
    assert groups["token-test-group"]["Description"] == "group for next-token listing"