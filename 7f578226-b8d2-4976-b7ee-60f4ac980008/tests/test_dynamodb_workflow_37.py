from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_recreate_after_put_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl35",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl35",
                 "--item", '{"pk":{"S":"keep"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl35",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode != 0
    assert "ResourceInUseException" in result.stderr
    resp = ddb_client.get_item(TableName="WfTbl35", Key={"pk": {"S": "keep"}})
    assert "Item" in resp
