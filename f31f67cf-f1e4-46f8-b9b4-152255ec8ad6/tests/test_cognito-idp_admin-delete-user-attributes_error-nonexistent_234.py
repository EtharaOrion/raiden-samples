def test_admin_delete_user_attributes_nonexistent_pool(cli, cognito, tmp_path):
    suffix = tmp_path.name
    live_pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"delete-attrs-live-{suffix}"},
    )["UserPool"]
    deleted_pool = cognito.rpc(
        "CreateUserPool",
        {"PoolName": f"delete-attrs-missing-{suffix}"},
    )["UserPool"]
    cognito.rpc("DeleteUserPool", {"UserPoolId": deleted_pool["Id"]})

    result = cli(
        "cognito-idp",
        "admin-delete-user-attributes",
        "--user-pool-id",
        deleted_pool["Id"],
        "--username",
        "nonexistent-user",
        "--user-attribute-names",
        '["email"]',
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    described = cognito.rpc(
        "DescribeUserPool",
        {"UserPoolId": live_pool["Id"]},
    )["UserPool"]
    assert described["Id"] == live_pool["Id"]
    assert described["Name"] == f"delete-attrs-live-{suffix}"