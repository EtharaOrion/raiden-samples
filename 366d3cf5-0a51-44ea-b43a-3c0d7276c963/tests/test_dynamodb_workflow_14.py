from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_composite_key_put_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf15",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf15",
                 "--item", '{"pk":{"S":"p"},"sk":{"S":"s"},"v":{"S":"data"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf15", Key={"pk": {"S": "p"}, "sk": {"S": "s"}})
    assert from_item(resp["Item"]) == {"pk": "p", "sk": "s", "v": "data"}
