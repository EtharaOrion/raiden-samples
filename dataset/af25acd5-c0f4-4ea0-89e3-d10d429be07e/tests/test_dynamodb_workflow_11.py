from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_query_after_cli_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "QCliTbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "QCliTbl" in ddb_client.list_tables()["TableNames"]

    result = cli("dynamodb", "put-item", "--table-name", "QCliTbl",
                 "--item", '{"pk":{"S":"only"},"n":{"N":"42"}}')
    assert result.returncode == 0

    resp = ddb_client.query(
        TableName="QCliTbl",
        KeyConditionExpression="pk = :v",
        ExpressionAttributeValues={":v": {"S": "only"}})
    natives = [from_item(it) for it in resp["Items"]]
    assert natives == [{"pk": "only", "n": 42}]
