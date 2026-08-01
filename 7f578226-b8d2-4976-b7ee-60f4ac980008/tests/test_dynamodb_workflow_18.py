from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_map_item_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl16",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl16",
                 "--item", '{"pk":{"S":"m1"},"meta":{"M":{"x":{"N":"1"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl16", Key={"pk": {"S": "m1"}})
    assert resp["Item"]["meta"]["M"]["x"]["N"] == "1"
