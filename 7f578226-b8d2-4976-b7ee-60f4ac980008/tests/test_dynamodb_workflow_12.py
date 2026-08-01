from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_number_item_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl10",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl10",
                 "--item", '{"pk":{"S":"num1"},"count":{"N":"12345"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl10", Key={"pk": {"S": "num1"}})
    assert resp["Item"]["count"]["N"] == "12345"
