from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_long_string_value(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Tbl_long1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    big = "x" * 500
    result = cli("dynamodb", "put-item", "--table-name", "Tbl_long1",
                 "--item", '{"pk":{"S":"lo1"},"blob":{"S":"%s"}}' % big)
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Tbl_long1", Key={"pk": {"S": "lo1"}})
    assert from_item(resp["Item"]) == {"pk": "lo1", "blob": big}
