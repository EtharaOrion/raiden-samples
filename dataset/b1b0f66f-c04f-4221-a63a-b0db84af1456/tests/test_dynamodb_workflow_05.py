from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_item_missing_table_fails(cli, ddb_client):
    result = cli(
        "dynamodb", "get-item",
        "--table-name", "MissingGetTableWF",
        "--key", '{"pk":{"S":"x"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
