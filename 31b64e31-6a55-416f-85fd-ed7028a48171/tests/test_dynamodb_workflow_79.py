from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_final_lifecycle_full_chain(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf80Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    assert "Wf80Tbl" in ddb_client.list_tables()["TableNames"]
    result = cli("dynamodb", "put-item", "--table-name", "Wf80Tbl",
                 "--item", '{"pk":{"S":"lc"},"stage":{"S":"created"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf80Tbl", Key={"pk": {"S": "lc"}})
    assert from_item(resp["Item"]) == {"pk": "lc", "stage": "created"}
    result = cli("dynamodb", "put-item", "--table-name", "Wf80Tbl",
                 "--item", '{"pk":{"S":"lc"},"stage":{"S":"updated"}}')
    assert result.returncode == 0
    resp = ddb_client.get_item(TableName="Wf80Tbl", Key={"pk": {"S": "lc"}})
    assert from_item(resp["Item"]) == {"pk": "lc", "stage": "updated"}
