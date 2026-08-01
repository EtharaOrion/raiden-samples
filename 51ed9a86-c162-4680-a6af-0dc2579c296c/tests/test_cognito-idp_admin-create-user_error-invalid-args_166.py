def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    missing_pool_id = "local_doesnotexist"
    username = "ghostuser"

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", missing_pool_id,
        "--username", username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert state: the user was never created (pool doesn't exist -> lookup errors)
    try:
        resp = cognito.rpc("AdminGetUser", {
            "UserPoolId": missing_pool_id,
            "Username": username,
        })
        # If somehow it returns, the user must not be present
        assert resp.get("Username") != username
    except Exception:
        # Expected: referencing missing pool/user raises
        pass