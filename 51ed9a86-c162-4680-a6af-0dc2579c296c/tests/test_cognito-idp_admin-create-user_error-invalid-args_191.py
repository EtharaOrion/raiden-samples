def test_admin_create_user_nonexistent_pool_error(cli, cognito):
    fake_pool_id = "local_nonexistentpool"
    username = "erroruser"

    # Ensure the pool truly does not exist by listing pools and checking absence.
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    existing_ids = {p["Id"] for p in listed.get("UserPools", [])}
    assert fake_pool_id not in existing_ids

    result = cli(
        "cognito-idp", "admin-create-user",
        "--user-pool-id", fake_pool_id,
        "--username", username,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # Assert no user was created anywhere for this fake pool (still nonexistent).
    listed_after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids_after = {p["Id"] for p in listed_after.get("UserPools", [])}
    assert fake_pool_id not in ids_after