Feature: Persistir texto ingresado por el usuario

  Scenario: El usuario ingresa un texto y aparece en la tabla
    Given la aplicacion esta disponible
    When el usuario envia el texto "Hola behave"
    Then la respuesta es exitosa
    And el texto "Hola behave" aparece en la pagina

  Scenario: Recargar la pagina no vuelve a guardar el texto
    Given la aplicacion esta disponible
    When el usuario envia el texto "Una sola vez"
    And el usuario recarga la pagina
    Then la respuesta es exitosa
    And el texto "Una sola vez" aparece una sola vez en la tabla

  Scenario: El usuario elimina un texto y desaparece de la tabla
    Given la aplicacion esta disponible
    When el usuario envia el texto "Texto a borrar"
    And el usuario elimina el texto "Texto a borrar"
    Then la respuesta es exitosa
    And el texto "Texto a borrar" no aparece en la pagina

  Scenario: Eliminar un texto no afecta a los demas
    Given la aplicacion esta disponible
    When el usuario envia el texto "Texto a borrar"
    And el usuario envia el texto "Texto que se queda"
    And el usuario elimina el texto "Texto a borrar"
    Then la respuesta es exitosa
    And el texto "Texto a borrar" no aparece en la pagina
    And el texto "Texto que se queda" aparece en la pagina

  Scenario: Health endpoint
    Given la aplicacion esta disponible
    When consulto el endpoint de health
    Then el estado es "ok"

  Scenario: Version endpoint
    Given la aplicacion esta disponible
    When consulto el endpoint de version
    Then la version es "10.3"
