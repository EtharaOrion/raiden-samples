from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_large_number(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf60",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf60",
                 "--item", '{"pk":{"S":"big"},"num":{"N":"123456789012345"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf60", Key={"pk": {"S": "big"}})
    assert resp["Item"]["num"] == {"N": "123456789012345"}
