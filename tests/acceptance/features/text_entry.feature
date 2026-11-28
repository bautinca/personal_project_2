Feature: Alta, baja y modificacion de textos ingresados por el usuario

  Scenario: El usuario ingresa un texto y aparece en la lista
    Given la aplicacion esta disponible
    When el usuario envia el texto "Hola behave"
    Then la respuesta es exitosa
    And el texto "Hola behave" aparece en la pagina

  Scenario: Recargar la pagina no vuelve a guardar el texto
    Given la aplicacion esta disponible
    When el usuario envia el texto "Una sola vez"
    And el usuario recarga la pagina
    Then la respuesta es exitosa
    And el texto "Una sola vez" aparece una sola vez en la lista

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

  Scenario: El usuario modifica un texto y se muestra el nuevo
    Given la aplicacion esta disponible
    When el usuario envia el texto "Texto original"
    And el usuario modifica el texto "Texto original" por "Texto corregido"
    Then la respuesta es exitosa
    And el texto "Texto corregido" aparece una sola vez en la lista
    And el texto "Texto original" no aparece en la pagina

  Scenario: Modificar un texto no afecta a los demas
    Given la aplicacion esta disponible
    When el usuario envia el texto "Texto a cambiar"
    And el usuario envia el texto "Texto que se queda"
    And el usuario modifica el texto "Texto a cambiar" por "Texto cambiado"
    Then la respuesta es exitosa
    And el texto "Texto cambiado" aparece una sola vez en la lista
    And el texto "Texto que se queda" aparece una sola vez en la lista
    And el texto "Texto a cambiar" no aparece en la pagina
