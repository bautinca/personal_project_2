Feature: Estado de la aplicacion

  Scenario: Health endpoint
    Given la aplicacion esta disponible
    When consulto el endpoint de health
    Then el estado es "ok"

  Scenario: Version endpoint
    Given la aplicacion esta disponible
    When consulto el endpoint de version
    Then la version es la definida en el archivo VERSION
