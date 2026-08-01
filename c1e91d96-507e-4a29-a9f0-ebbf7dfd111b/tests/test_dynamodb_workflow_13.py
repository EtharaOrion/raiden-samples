from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_number_types_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfNum1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfNum1",
                 "--item", '{"pk":{"S":"n"},"i":{"N":"42"},"f":{"N":"3.5"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfNum1", Key={"pk": {"S": "n"}})
    got = from_item(resp["Item"])
    assert got["i"] == 42
    assert got["f"] == 3.5
