from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_missing_table_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfPutT1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WfPutT1" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "put-item", "--table-name", "WfPutNoSuch1",
                 "--item", '{"pk":{"S":"z"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
