def test_delete_user_pool_nonexistent_pool_error(cli, cognito):
    fake_pool_id = "local_nonexistent999"

    result = cli("cognito-idp", "delete-user-pool", "--user-pool-id", fake_pool_id)

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    listing = cognito.rpc("ListUserPools", {"MaxResults": 60})
    pool_ids = [p["Id"] for p in listing.get("UserPools", [])]
    assert fake_pool_id not in pool_ids