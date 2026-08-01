from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_number_set(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "WfNS1",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "WfNS1",
                 "--item", '{"pk":{"S":"ns"},"nums":{"NS":["1","2","3"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="WfNS1", Key={"pk": {"S": "ns"}})
    got = from_item(resp["Item"])
    assert set(got["nums"]) == {1, 2, 3}
