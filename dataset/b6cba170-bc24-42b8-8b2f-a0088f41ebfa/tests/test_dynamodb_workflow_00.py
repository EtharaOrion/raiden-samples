from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_get(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WFCreatePutGet",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "WFCreatePutGet" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "put-item", "--table-name", "WFCreatePutGet",
                 "--item", '{"pk":{"S":"a1"},"n":{"N":"5"}}')
    assert result.returncode == 0

    resp = ddb_client.get_item(TableName="WFCreatePutGet", Key={"pk": {"S": "a1"}})
    assert "Item" in resp
    item = from_item(resp["Item"])
    assert item["pk"] == "a1"
    assert item["n"] == 5
