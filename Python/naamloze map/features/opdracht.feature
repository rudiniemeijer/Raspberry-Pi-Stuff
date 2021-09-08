Feature: Een wazige opdracht die niemand snapt

  Met enkele halve aanwijzingen een bestandje vullen met regels
  en dan controleren of de regels er inderdaad in zitten.

Scenario: Create a file
    Given There is an empty text file available to us
    When I open this file
    And I write the following table in it
      | course          | participants |
      | Behave          | 213          |
      | Cucumber        | 0            |
      | Robot Framework | 42           |
    Then This file has 3 lines in it

Scenario: Append to an existing file
    Given This file has 3 lines in it
    When I append to this file
    And write the following table in it
      | course          | participants |
      | TestComplete    | 305          |
      | Katalon Studio  | 12           |
      | Postman         | 100          |
    Then This file has 6 lines in it