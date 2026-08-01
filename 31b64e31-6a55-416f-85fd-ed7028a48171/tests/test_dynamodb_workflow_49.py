from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddbclient_create_cli_put_get(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Wf50Tbl",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    result = cli("dynamodb", "put-item", "--table-name", "Wf50Tbl",
                 "--item", '{"pk":{"S":"viacli"},"v":{"S":"ok"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf50Tbl", Key={"pk": {"S": "viacli"}})
    assert from_item(resp["Item"]) == {"pk": "viacli", "v": "ok"}
