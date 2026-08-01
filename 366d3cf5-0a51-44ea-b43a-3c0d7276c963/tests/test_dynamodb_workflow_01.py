from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_deleteitem(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf2",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf2",
                 "--item", '{"pk":{"S":"x"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf2",
                 "--key", '{"pk":{"S":"x"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf2", Key={"pk": {"S": "x"}})
    assert "Item" not in resp
