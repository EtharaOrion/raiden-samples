def test_admin_create_user_invalid_user_attributes_json(cli, cognito):
    import uuid

    pool_name = f"invalid-args-{uuid.uuid4().hex}"
    username = f"user-{uuid.uuid4().hex}"

    created = cognito.rpc("CreateUserPool", {"PoolName": pool_name})
    pool_id = created["UserPool"]["Id"]

    result = cli(
        "cognito-idp",
        "admin-create-user",
        "--user-pool-id",
        pool_id,
        "--username",
        username,
        "--user-attributes",
        "{not valid json",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "Invalid JSON" in result.stderr

    described = cognito.rpc("DescribeUserPool", {"UserPoolId": pool_id})
    assert described["UserPool"]["Name"] == pool_name

    users = cognito.rpc("ListUsers", {"UserPoolId": pool_id})["Users"]
    assert all(user["Username"] != username for user in users)