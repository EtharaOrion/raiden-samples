from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multiple_tables_get_ghost_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf64Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf64Tbl",
                 "--item", '{"pk":{"S":"a"},"v":{"S":"b"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "get-item", "--table-name", "Wf64Ghost",
                 "--key", '{"pk":{"S":"a"}}')
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    resp = ddb_client.get_item(TableName="Wf64Tbl", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"]) == {"pk": "a", "v": "b"}
