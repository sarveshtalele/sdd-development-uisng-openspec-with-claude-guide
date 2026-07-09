## ADDED Requirements

### Requirement: Trip parameters via CLI arguments
The system SHALL accept a destination, a number of trip days, and optional traveler
preferences (pace, interests, budget level) as command-line arguments.

#### Scenario: Valid required arguments provided
- **WHEN** the user runs the tool with a destination and a positive integer number of
  days
- **THEN** the system accepts the input and proceeds to itinerary generation

#### Scenario: Required argument missing
- **WHEN** the user runs the tool without a destination or without a number of days
- **THEN** the system prints a usage error identifying the missing argument and exits
  without attempting to generate an itinerary

#### Scenario: Invalid number of days
- **WHEN** the user provides a number of days that is zero, negative, or not a whole
  number
- **THEN** the system prints an error identifying the problem and exits without
  attempting to generate an itinerary

### Requirement: Configuration read from environment variables
The system SHALL read the OpenAI-compatible API key, base URL, and model name from
environment variables, and SHALL NOT accept the API key as a command-line argument.

#### Scenario: API key present
- **WHEN** the `OPENAI_API_KEY` environment variable is set
- **THEN** the system uses it to authenticate the itinerary-generation request

#### Scenario: API key missing
- **WHEN** the `OPENAI_API_KEY` environment variable is not set
- **THEN** the system prints an error naming `OPENAI_API_KEY` specifically and exits
  before attempting any network call

#### Scenario: Base URL not provided
- **WHEN** the `OPENAI_BASE_URL` environment variable is not set
- **THEN** the system falls back to the default OpenAI API endpoint

### Requirement: Structured itinerary generation
The system SHALL request a structured, day-by-day itinerary from the configured model,
covering exactly the requested number of days.

#### Scenario: Successful generation
- **WHEN** the model returns a well-formed itinerary covering the requested number of
  days
- **THEN** the system accepts the result and proceeds to rendering

#### Scenario: Malformed model response
- **WHEN** the model's response cannot be parsed as the expected itinerary shape, or is
  missing one or more requested days
- **THEN** the system prints a validation error describing what was wrong and does not
  render a partial or malformed itinerary

### Requirement: Readable terminal rendering
The system SHALL render a validated itinerary as readable, day-ordered plain text in
the terminal.

#### Scenario: Rendering a validated itinerary
- **WHEN** a valid, validated itinerary is available
- **THEN** the system prints each day in order, with that day's activities listed in
  the time order the model provided
