## ADDED Requirements

### Requirement: Graceful handling of API-level request failures
The system SHALL catch failures raised by the configured model client during itinerary
generation (including authentication failures, rate limiting, and connection failures)
and SHALL exit with a clear, single-line error message rather than an unhandled
exception traceback.

#### Scenario: API request fails
- **WHEN** the configured model client raises an error while requesting the itinerary
  (for example, an invalid API key or a network failure)
- **THEN** the system prints an error describing that the request failed and exits
  without printing a Python stack trace or attempting to render a partial itinerary
