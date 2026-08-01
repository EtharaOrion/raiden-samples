def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    fake_pool_id = "local_nonexistent999"

    # Ensure the pool truly does not exist by asserting DescribeUserPool fails
    describe_failed = False
    try:
        cognito.rpc("DescribeUserPool", {"UserPoolId": fake_pool_id})
    except Exception:
        describe_failed = True
    assert describe_failed

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", fake_pool_id,
        "--username", "someuser",
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no user was created (pool doesn't exist -> ListUsers must fail too)
    list_failed = False
    try:
        cognito.rpc("ListUsers", {"UserPoolId": fake_pool_id})
    except Exception:
        list_failed = True
    assert list_failed