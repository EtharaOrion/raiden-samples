def test_delete_group_missing_user_pool_id(cli, cognito):
    pool = cognito.rpc("CreateUserPool", {"PoolName": "delete-group-invalid-args-pool"})
    pool_id = pool["UserPool"]["Id"]
    group_name = "group-to-preserve"

    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Must remain after rejected delete",
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
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
    assert group["Description"] == "Must remain after rejected delete"