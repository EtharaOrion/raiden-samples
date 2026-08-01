from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddb_created_table_cli_put(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Tbl_ddbmk1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_ddbmk1",
                 "--item", '{"pk":{"S":"dm1"},"v":{"N":"99"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_ddbmk1", Key={"pk": {"S": "dm1"}})
    assert from_item(resp["Item"]) == {"pk": "dm1", "v": 99}
