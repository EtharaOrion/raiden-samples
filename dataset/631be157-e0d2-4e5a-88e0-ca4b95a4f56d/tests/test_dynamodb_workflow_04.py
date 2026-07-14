from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_getitem_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "get-item", "--table-name", "Wf_NoSuchTable_G",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
