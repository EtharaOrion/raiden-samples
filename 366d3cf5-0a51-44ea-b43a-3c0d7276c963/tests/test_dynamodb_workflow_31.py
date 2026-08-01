from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_create_with_gsi_and_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf32",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"gsk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--global-secondary-indexes",
                 '[{"IndexName":"gsi1","KeySchema":[{"AttributeName":"gsk","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"}}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf32" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf32",
                 "--item", '{"pk":{"S":"a"},"gsk":{"S":"g"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf32", Key={"pk": {"S": "a"}})
    assert from_item(resp["Item"]) == {"pk": "a", "gsk": "g"}
