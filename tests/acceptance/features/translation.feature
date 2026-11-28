Feature: Traduccion de textos al ingles

  Scenario: El usuario traduce un texto
    Given la aplicacion esta disponible
    When el usuario envia el texto "Hola mundo"
    And el usuario traduce el texto "Hola mundo"
    Then la respuesta es exitosa
    And se muestra la traduccion de "Hola mundo"
    And el texto "Hola mundo" aparece en la pagina

  Scenario: La traduccion no se guarda
    Given la aplicacion esta disponible
    When el usuario envia el texto "Hola mundo"
    And el usuario traduce el texto "Hola mundo"
    And el usuario vuelve a la pagina principal
    Then la respuesta es exitosa
    And no se muestra la traduccion de "Hola mundo"

  Scenario: El servicio de traduccion no esta disponible
    Given la aplicacion esta disponible
    And el servicio de traduccion no esta disponible
    When el usuario envia el texto "Hola mundo"
    And el usuario traduce el texto "Hola mundo"
    Then se muestra el aviso "No se pudo traducir"
    And el texto "Hola mundo" aparece en la pagina
