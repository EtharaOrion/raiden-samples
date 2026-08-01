from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_multiple_puts_then_selective_delete(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf80",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    for k in ("a", "b", "c"):
        result = cli("dynamodb", "put-item", "--table-name", "Wf80", "--item", '{"pk":{"S":"%s"}}' % k)
        assert result.returncode == 0
    result = cli("dynamodb", "delete-item", "--table-name", "Wf80", "--key", '{"pk":{"S":"b"}}')
    assert result.returncode == 0
    assert "Item" in ddb_client.get_item(TableName="Wf80", Key={"pk": {"S": "a"}})
    assert "Item" not in ddb_client.get_item(TableName="Wf80", Key={"pk": {"S": "b"}})
    assert "Item" in ddb_client.get_item(TableName="Wf80", Key={"pk": {"S": "c"}})
