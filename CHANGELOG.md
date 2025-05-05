# Changelog

## [Unreleased]
### Added
- Explicit age input fields for both participants
- Age information is now incorporated directly into persona profiles
- Improved theme/location handling in agent initialization
- Enhanced error handling and default values
- Better error diagnostics for model selection issues

### Changed
- Updated UI with specific age inputs (default 28 for Person A, 30 for Person B)
- Modified profile placeholders to remove age references (since it's now a separate field)
- Reduced text area height slightly to accommodate the new age inputs
- Added age information to test simulations
- Updated tests to support the new age parameters
- Improved model selection help text to clarify model name/provider format

### Fixed
- Proper handling of theme/location context in agent initialization
- Fixed initialization logic for name fields with empty values
- Fixed model selection to correctly extract provider from the format "model_name [provider]"
- Ensured proper service name passing to EDSL functions
- Resolved conflict in default model selection logic