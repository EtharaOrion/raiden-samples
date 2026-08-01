def test_get_group_rejects_empty_group_name(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "get-group-empty-name-test"},
    )["UserPool"]
    pool_id = pool["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "existing-group",
            "Description": "sentinel group",
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        "",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "InvalidParameterException" in result.stderr
        or "Invalid length" in result.stderr
    )

    groups = cognito.rpc("ListGroups", {"UserPoolId": pool_id})["Groups"]
    assert any(
        group["GroupName"] == "existing-group"
        and group.get("Description") == "sentinel group"
        for group in groups
    )