from _ddb_http import to_item, from_item, to_av, from_av


from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_get_after_two_puts_different_keys(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf36Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf36Tbl",
                 "--item", '{"pk":{"S":"k1"},"v":{"S":"one"}}')
    assert result.returncode == 0
    result = cli("dynamodb", "put-item", "--table-name", "Wf36Tbl",
                 "--item", '{"pk":{"S":"k2"},"v":{"S":"two"}}')
    assert result.returncode == 0
    r1 = ddb_client.get_item(TableName="Wf36Tbl", Key={"pk": {"S": "k1"}})
    r2 = ddb_client.get_item(TableName="Wf36Tbl", Key={"pk": {"S": "k2"}})
    assert from_item(r1["Item"]) == {"pk": "k1", "v": "one"}
    assert from_item(r2["Item"]) == {"pk": "k2", "v": "two"}
