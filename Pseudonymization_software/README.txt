# Pseudonymization Tool README

## Disclaimer
This software was developed solely for thesis study purposes and may not be complete or bug-free. The author does not guarantee support or fixes unless a reasonable request is made. Users should exercise caution and not rely on this tool for comprehensive privacy protection in a production environment.

## Overview
The Pseudonymization Tool is designed to anonymize sensitive information in documents by identifying and replacing personal identifiers with pseudonyms. This software is essential for maintaining privacy and complying with data protection regulations.

## Components
The software package consists of several Python files, each handling a specific part of the process:

- `main.py`: This is the entry point of the software. It orchestrates the flow of data between modules.
- `entity_recognizer.py`: Contains the logic to detect personal identifiers in the text.
- `memory.py`: Manages the mappings between original identifiers and their pseudonyms.
- `pdf_anonymizer.py`: Handles the reading, processing, and anonymizing of PDF files.
- `readers.py`: Provides functionality to read different types of input files.

## Prerequisites
Before running the pseudonymization software, ensure you have the following installed:
- Python 3.7 or higher
- Necessary Python libraries as specified in `requirements.txt`

## Installation
To install the software, follow these steps:
1. Clone the repository or download the zip file to your local machine.
2. Navigate to the directory containing the software files.
3. Install the required dependencies:

## Usage
To use the software, run the `main.py` script.
### Further instructions:
- no commas are allowed in the entity names
- only these entities are can be pseudonymized: ["EMAIL_ADDRESS", "LOCATION", "PERSON", "PHONE_NUMBER", "ORGANIZATION"]


## License
This software is provided under MIT license.
