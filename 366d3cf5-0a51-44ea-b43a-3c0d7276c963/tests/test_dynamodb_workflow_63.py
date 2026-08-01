from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_numberset_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf64",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf64",
                 "--item", '{"pk":{"S":"ns"},"nums":{"NS":["1","2","3"]}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf64", Key={"pk": {"S": "ns"}})
    assert set(resp["Item"]["nums"]["NS"]) == {"1", "2", "3"}
