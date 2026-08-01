from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_large_number_readback(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfTbl30",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfTbl30",
                 "--item", '{"pk":{"S":"big"},"n":{"N":"9007199254740993"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfTbl30", Key={"pk": {"S": "big"}})
    assert resp["Item"]["n"]["N"] == "9007199254740993"
