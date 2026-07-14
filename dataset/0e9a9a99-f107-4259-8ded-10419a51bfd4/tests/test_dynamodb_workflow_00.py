from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get_lifecycle(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "LifecycleTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "LifecycleTbl" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "put-item", "--table-name", "LifecycleTbl",
                 "--item", '{"pk":{"S":"item1"},"n":{"N":"5"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="LifecycleTbl", Key={"pk": {"S": "item1"}})
    assert "Item" in resp
    assert from_item(resp["Item"]) == {"pk": "item1", "n": 5}
