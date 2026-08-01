from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_put_number_types(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf19",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf19",
                 "--item", '{"pk":{"S":"num"},"count":{"N":"42"},"price":{"N":"9"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf19", Key={"pk": {"S": "num"}})
    assert resp["Item"]["count"] == {"N": "42"}
    assert resp["Item"]["price"] == {"N": "9"}
