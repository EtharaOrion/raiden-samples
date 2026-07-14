from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_missing_fails(cli, ddb_client):
    result = cli("dynamodb", "delete-table", "--table-name", "Wf_NoSuchTable_ZZZ")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
