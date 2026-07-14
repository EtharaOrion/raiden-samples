from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get_lifecycle(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfLife1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WfLife1" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "put-item", "--table-name", "WfLife1",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"7"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="WfLife1", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    from _ddb_http import from_item
    assert from_item(resp["Item"]) == {"pk": "a1", "n": 7}
