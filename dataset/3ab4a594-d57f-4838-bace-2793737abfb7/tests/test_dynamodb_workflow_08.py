from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_conditional_unchanged(cli, ddb_client, tmp_path):
    result = cli("dynamodb", "create-table", "--table-name", "Wf9Tbl",
                 "--attribute-definitions", '[{"AttributeName":"pk","AttributeType":"S"}]',
                 "--key-schema", '[{"AttributeName":"pk","KeyType":"HASH"}]',
                 "--billing-mode", "PAY_PER_REQUEST")
    assert result.returncode == 0

    result = cli("dynamodb", "put-item", "--table-name", "Wf9Tbl",
                 "--item", '{"pk":{"S":"u1"},"n":{"N":"1"}}')
    assert result.returncode == 0

    result = cli("dynamodb", "update-item", "--table-name", "Wf9Tbl",
                 "--key", '{"pk":{"S":"u1"}}',
                 "--update-expression", "SET n = :new",
                 "--expression-attribute-values", '{":new":{"N":"99"},":chk":{"N":"5"}}',
                 "--condition-expression", "n = :chk")
    assert result.returncode != 0
    assert "ConditionalCheckFailedException" in result.stderr

    from _ddb_http import from_item
    resp = ddb_client.get_item(TableName="Wf9Tbl", Key={"pk": {"S": "u1"}})
    assert from_item(resp["Item"])["n"] == 1
