from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrite_shrinks_item(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf36",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf36",
                 "--item", '{"pk":{"S":"s"},"a":{"S":"1"},"b":{"S":"2"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf36",
                 "--item", '{"pk":{"S":"s"},"a":{"S":"9"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf36", Key={"pk": {"S": "s"}})
    assert from_item(resp["Item"]) == {"pk": "s", "a": "9"}
