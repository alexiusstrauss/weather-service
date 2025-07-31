Feature: Weather API
  As a user of the weather API
  I want to get current weather information for cities
  So that I can make decisions based on weather conditions

  Background:
    Given the weather service is running
    And the API is accessible

  Scenario: Get weather for a valid city
    Given I have a valid city name "São Paulo"
    When I request weather information for the city
    Then I should receive weather data
    And the response should contain temperature
    And the response should contain description
    And the response should contain city name "São Paulo"

  Scenario: Get weather for an invalid city
    Given I have an invalid city name "NonExistentCity123"
    When I request weather information for the city
    Then I should receive an error response
    And the error should indicate city not found

  Scenario: Request weather without city parameter
    Given the weather service is running
    And the API is accessible
    When I request weather information without city parameter
    Then I should receive a bad request error
    And the error should indicate missing city parameter

  Scenario: Weather data is cached
    Given I have a valid city name "Rio de Janeiro"
    When I request weather information for the city
    Then I should receive weather data
    And the cached flag should be false
    When I request weather information for the same city again
    Then I should receive weather data
    And the cached flag should be true

  Scenario: Weather history is saved
    Given I have a valid city name "Brasília"
    When I request weather information for the city
    Then I should receive weather data
    When I request weather history for the city
    Then I should receive history data
    And the history should contain at least 1 entry

  Scenario: Rate limiting blocks excess requests
    Given the rate limit is set to 5 requests per minute
    When I make 6 requests in quick succession
    Then the first 5 requests should succeed
    And the 6th request should be rate limited
    And I should receive a 429 status code

  Scenario: Cache invalidation works
    Given I have a valid city name "Belo Horizonte"
    And weather data is cached for the city
    When I invalidate the cache for the city
    And I request weather information for the city
    Then I should receive fresh weather data
    And the cached flag should be false
