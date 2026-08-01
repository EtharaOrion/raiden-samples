def test_list_groups_rejects_unknown_flag(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "list-groups-invalid-args-pool"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "Group preserved after invalid CLI invocation",
        },
    )

    result = cli(
        "cognito-idp",
        "list-groups",
        "--user-pool-id",
        pool_id,
        "--not-a-real-flag",
        "x",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Unknown options" in result.stderr

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert any(
        group["GroupName"] == "existing-group"
        and group["UserPoolId"] == pool_id
        for group in groups
    )