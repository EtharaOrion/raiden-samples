from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_describe_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "describe-table", "--table-name", "NoSuchTblX2")
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
