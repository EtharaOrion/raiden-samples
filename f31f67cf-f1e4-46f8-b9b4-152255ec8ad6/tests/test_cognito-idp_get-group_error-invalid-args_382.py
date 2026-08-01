def test_get_group_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": "get-group-invalid-args-pool"},
    )["UserPool"]
    pool_id = pool["Id"]
    group_name = "get-group-invalid-args-group"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Group preserved after invalid get-group invocation",
        },
    )

    result = cli(
        "cognito-idp",
        "get-group",
        "--group-name",
        group_name,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()
    assert "--user-pool-id" in result.stderr

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "Group preserved after invalid get-group invocation"