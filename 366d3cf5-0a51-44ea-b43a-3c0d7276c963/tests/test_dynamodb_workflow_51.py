from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_updates_multiple_attrs(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf52",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf52",
                 "--item", '{"pk":{"S":"u"},"a":{"N":"1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf52",
                 "--item", '{"pk":{"S":"u"},"a":{"N":"2"},"b":{"S":"added"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf52", Key={"pk": {"S": "u"}})
    assert from_item(resp["Item"]) == {"pk": "u", "a": 2, "b": "added"}
