from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_put_two_readback_both(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf57",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf57", "--item", '{"pk":{"S":"x"},"v":{"S":"vx"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf57", "--item", '{"pk":{"S":"y"},"v":{"S":"vy"}}')
    assert result.returncode == 0
    assert from_item(ddb_client.get_item(TableName="Wf57", Key={"pk": {"S": "x"}})["Item"])["v"] == "vx"
    assert from_item(ddb_client.get_item(TableName="Wf57", Key={"pk": {"S": "y"}})["Item"])["v"] == "vy"
