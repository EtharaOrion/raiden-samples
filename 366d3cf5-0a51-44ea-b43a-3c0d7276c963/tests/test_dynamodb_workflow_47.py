from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_lsi_create_put(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf48",
                 "--attribute-definitions",
                 '[{"AttributeName":"pk","AttributeType":"S"},{"AttributeName":"sk","AttributeType":"S"},{"AttributeName":"lsk","AttributeType":"S"}]',
                 "--key-schema",
                 '[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"sk","KeyType":"RANGE"}]',
                 "--local-secondary-indexes",
                 '[{"IndexName":"lsi1","KeySchema":[{"AttributeName":"pk","KeyType":"HASH"},{"AttributeName":"lsk","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"}}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf48" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf48",
                 "--item", '{"pk":{"S":"p"},"sk":{"S":"s"},"lsk":{"S":"l"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf48", Key={"pk": {"S": "p"}, "sk": {"S": "s"}})
    assert from_item(resp["Item"]) == {"pk": "p", "sk": "s", "lsk": "l"}
