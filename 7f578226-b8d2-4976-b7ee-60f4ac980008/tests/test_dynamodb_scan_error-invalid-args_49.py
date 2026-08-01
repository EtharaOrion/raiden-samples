from _ddb_http import to_item, from_item, to_av, from_av


def test_scan_nonexistent_table_error(cli, ddb_client):
    result = cli(
        "dynamodb", "scan",
        "--table-name", "NoSuchTableForScan",
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr