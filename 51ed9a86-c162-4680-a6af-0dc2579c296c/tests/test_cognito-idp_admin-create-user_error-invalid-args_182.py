def test_admin_create_user_nonexistent_pool_errors(cli, cognito):
    # Reference a user pool that does not exist -> ResourceNotFoundException
    missing_pool_id = "local_doesnotexist"
    username = "ghost-user"

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", missing_pool_id,
        "--username", username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no such user exists (pool itself is absent so lookup must fail too)
    err = None
    try:
        cognito.rpc("AdminGetUser", {"UserPoolId": missing_pool_id, "Username": username})
    except Exception as e:
        err = str(e)
    assert err is not None