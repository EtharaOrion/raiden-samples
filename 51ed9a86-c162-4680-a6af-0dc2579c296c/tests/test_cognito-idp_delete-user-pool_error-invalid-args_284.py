def test_delete_user_pool_nonexistent_pool_errors(cli, cognito):
    # Reference a pool id that does not exist -> ResourceNotFoundException.
    missing_pool_id = "local_nonexistent999"

    # Ensure the pool is indeed absent from the account.
    listed = cognito.rpc("ListUserPools", {"MaxResults": 60})
    existing_ids = {p["Id"] for p in listed.get("UserPools", [])}
    assert missing_pool_id not in existing_ids

    result = cli(
        "cognito-idp",
        "delete-user-pool",
        "--user-pool-id",
        missing_pool_id,
    )

    assert result.returncode != 0
    assert not result.stdout.strip(), result.stdout
    assert "ResourceNotFoundException" in result.stderr

    # State remains unchanged: still not present.
    listed_after = cognito.rpc("ListUserPools", {"MaxResults": 60})
    ids_after = {p["Id"] for p in listed_after.get("UserPools", [])}
    assert missing_pool_id not in ids_after