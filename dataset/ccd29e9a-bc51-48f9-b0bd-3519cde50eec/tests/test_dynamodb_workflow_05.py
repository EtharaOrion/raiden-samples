from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_deletetable_missing_fails(ddb_client, cli, tmp_path):
    result = cli("dynamodb", "delete-table", "--table-name", "NoSuchTableDrop")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
