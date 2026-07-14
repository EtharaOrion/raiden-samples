from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deleteitem_missing_table_fails(cli, ddb_client):
    result = cli(
        "dynamodb", "delete-item",
        "--table-name", "Wf_MissingDelTable_ZZZ",
        "--key", '{"pk":{"S":"a"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
