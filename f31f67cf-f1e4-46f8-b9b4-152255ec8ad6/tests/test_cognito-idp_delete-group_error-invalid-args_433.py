def test_delete_group_missing_group_name_preserves_group(cli, cognito, tmp_path):
    pool_name = "delete-group-invalid-" + tmp_path.name
    pool = cognito.rpc("CreateUserPool", {"PoolName": pool_name})["UserPool"]
    pool_id = pool["Id"]

    group_name = "group-to-preserve"
    cognito.rpc(
        "CreateGroup",
        {
            "UserPoolId": pool_id,
            "GroupName": group_name,
            "Description": "Must remain after invalid delete request",
        },
    )

    result = cli(
        "cognito-idp",
        "delete-group",
        "--user-pool-id",
        pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "required" in result.stderr.lower()

    group = cognito.rpc(
        "GetGroup",
        {"UserPoolId": pool_id, "GroupName": group_name},
    )["Group"]
    assert group["GroupName"] == group_name
    assert group["UserPoolId"] == pool_id
    assert group["Description"] == "Must remain after invalid delete request"