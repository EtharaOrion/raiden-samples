from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_ddb_seed_then_cli_overwrite(cli, ddb_client, tmp_path):
    ddb_client.create_table(
        TableName="Tbl_seedcli1",
        AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST")
    ddb_client.put_item(TableName="Tbl_seedcli1",
                        Item={"pk": {"S": "sc1"}, "v": {"S": "old"}})
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_seedcli1",
                 "--item", '{"pk":{"S":"sc1"},"v":{"S":"new"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_seedcli1", Key={"pk": {"S": "sc1"}})
    assert from_item(resp["Item"]) == {"pk": "sc1", "v": "new"}
