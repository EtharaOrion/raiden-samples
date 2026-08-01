from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_many_then_delete_all(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf34",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for i in range(4):
        result = cli("dynamodb", "put-item", "--table-name", "Wf34", "--item", '{"pk":{"S":"i%d"}}' % i)
        assert result.returncode == 0
    for i in range(4):
        result = cli("dynamodb", "delete-item", "--table-name", "Wf34", "--key", '{"pk":{"S":"i%d"}}' % i)
        assert result.returncode == 0
    for i in range(4):
        assert "Item" not in ddb_client.get_item(TableName="Wf34", Key={"pk": {"S": "i%d" % i}})
