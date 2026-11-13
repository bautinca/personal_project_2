Feature: Persistir texto ingresado por el usuario

  Scenario: El usuario ingresa un texto y aparece en la tabla
    Given la aplicacion esta disponible
    When el usuario envia el texto "Hola behave"
    Then la respuesta es exitosa
    And el texto "Hola behave" aparece en la pagina

  Scenario: Health endpoint
    Given la aplicacion esta disponible
    When consulto el endpoint de health
    Then el estado es "ok"

  Scenario: Version endpoint
    Given la aplicacion esta disponible
    When consulto el endpoint de version
    Then la version es "10.3"
