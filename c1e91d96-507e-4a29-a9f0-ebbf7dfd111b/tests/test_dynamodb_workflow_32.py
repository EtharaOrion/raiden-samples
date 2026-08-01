from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_large_string_value(cli, ddb_client, tmp_path):
    big = "x" * 500
    result = cli("dynamodb", "create-table", "--table-name", "WfBig1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfBig1",
                 "--item", '{"pk":{"S":"big"},"blob":{"S":"%s"}}' % big)
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfBig1", Key={"pk": {"S": "big"}})
    assert from_item(resp["Item"])["blob"] == big
