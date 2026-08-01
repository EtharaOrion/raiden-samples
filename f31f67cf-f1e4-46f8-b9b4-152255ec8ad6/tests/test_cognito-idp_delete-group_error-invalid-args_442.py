def test_delete_group_rejects_empty_group_name(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "group-that-must-remain",
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
        "--group-name",
        "",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert (
        "InvalidParameterException" in result.stderr
        or "Parameter validation failed" in result.stderr
    )

    group = cognito.rpc(
        "GetGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": "group-that-must-remain",
        },
    )["Group"]
    assert group["GroupName"] == "group-that-must-remain"
    assert group["UserPoolId"] == pool_id