from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_map_attribute_roundtrip(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_map1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_map1",
                 "--item", '{"pk":{"S":"m1"},"meta":{"M":{"x":{"N":"1"},"y":{"S":"z"}}}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_map1", Key={"pk": {"S": "m1"}})
    assert from_item(resp["Item"]) == {"pk": "m1", "meta": {"x": 1, "y": "z"}}
