from _ddb_http import to_item, from_item, to_av, from_av


def test_workflow_update_missing_table_no_create(cli, ddb_client, tmp_path):
    result = cli(
        "dynamodb", "update-item", "--table-name", "Wf47Ghost",
        "--key", '{"pk":{"S":"a"}}',
        "--update-expression", "SET v = :v",
        "--expression-attribute-values", '{":v":{"S":"x"}}',
    )
    assert result.returncode != 0
    assert "ResourceNotFoundException" in result.stderr
    assert "Wf47Ghost" not in ddb_client.list_tables()["TableNames"]
