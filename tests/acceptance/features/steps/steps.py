from behave import given, when, then


@given("la aplicacion esta disponible")
def step_app_available(context):
    assert context.client is not None


@when('el usuario envia el texto "{text}"')
def step_send_text(context, text):
    context.response = context.client.post("/", data={"text": text})


@when("consulto el endpoint de health")
def step_health(context):
    context.response = context.client.get("/health")


@when("consulto el endpoint de version")
def step_version(context):
    context.response = context.client.get("/version")


@then("la respuesta es exitosa")
def step_ok(context):
    assert context.response.status_code == 200


@then('el texto "{text}" aparece en la pagina')
def step_text_in_page(context, text):
    assert text in context.response.text


@then('el estado es "{status}"')
def step_status(context, status):
    assert context.response.json()["status"] == status


@then('la version es "{version}"')
def step_version_value(context, version):
    assert context.response.json()["version"] == version
