from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_delete_condition_fails(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfDelCond1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    ddb_client.put_item(TableName="WfDelCond1", Item={"pk": {"S": "dc1"}, "v": {"N": "1"}})
    result = cli("dynamodb", "delete-item", "--table-name", "WfDelCond1",
                 "--key", '{"pk":{"S":"dc1"}}',
                 "--condition-expression", "v = :x",
                 "--expression-attribute-values", '{":x":{"N":"999"}}')
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr
    resp = ddb_client.get_item(TableName="WfDelCond1", Key={"pk": {"S": "dc1"}})
    assert "Item" in resp
