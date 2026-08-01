from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_overwrite_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf9Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf9Tbl",
                 "--item", '{"pk":{"S":"o1"},"v":{"S":"v1"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf9Tbl",
                 "--item", '{"pk":{"S":"o1"},"v":{"S":"v2"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf9Tbl", Key={"pk": {"S": "o1"}})
    assert from_item(resp["Item"]) == {"pk": "o1", "v": "v2"}
