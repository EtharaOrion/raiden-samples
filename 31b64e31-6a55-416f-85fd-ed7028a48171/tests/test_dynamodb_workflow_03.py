from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_get_missing_table(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "put-item", "--table-name", "WfNoTbl4",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
