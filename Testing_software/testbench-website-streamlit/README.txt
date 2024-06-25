# Streamlit Webpage for Testing Purposes

This repository contains the code for a Streamlit webpage, designed solely for internal testing and development use. The codebase includes various components that support database management, document handling, and language model setup.

## Contents
- `Home.py` - Main entry script for the Streamlit webpage.
- `1_Database_and_test_manager.py` - Handles database operations and test management.
- `2_Doc_and_text_handling.py` - Manages document processing and text operations.
- `4_LLM_setup.py` - Sets up language learning models for testing.
- `5_#1_test_-_LLM_only.py` - Tests language learning models in isolation.
- `6_#2_test_-_basic_semantics.py` - Tests basic semantic operations.

## Installation

To get started with this project, you will need Python 3.x and Streamlit installed on your machine.

1. Clone this repository to your local machine

2. Install the required Python packages

3. Run the Streamlit application

## Usage

After installation, navigate to `localhost:8501` in your web browser to view the webpage.

## Disclaimer

This code was originally developed for internal testing and not intended for production use. As such:

- The webpage may contain bugs and unfinished features.
- The instructions provided in this README are not exhaustive and were not finalized as the project was not planned to be published.
- No support, bug fixes, or updates will be provided.

This project is provided as-is, and usage is at your own risk.



#READ-ME for LLM Testbench Application (auto-generated with GPT-4)

## Overview
This application is designed to provide a secure and interactive platform for testing the capabilities of Large Language Models (LLMs), specifically focusing on analyzing conflicts from construction industry documents. It features a login system for authentication, various pages for conducting tests, instructions for users to follow, a comprehensive database management system, a document loader page for handling and analyzing documents, and a dedicated page for querying LLMs with custom or predefined prompts. The application is built using Streamlit, making it web-friendly and easy to use.

## Features
- **Secure Login System**: Ensures that only authorized users can access the testbench.
- **Dynamic User Interface**: Offers a wide layout with a welcoming page, sidebar for navigation, and multiple pages dedicated to different aspects of the testing process including a document loader page and an LLM query page.
- **LLM Testing Framework**: Facilitates testing LLMs, such as OpenAI's GPT-4, for analyzing conflicts in construction industry documents. Users can interact with the LLM using custom or predefined prompts.
- **Database Management**: Allows users to set up and manage database connections for storing test results, with support for both MySQL and CSV storage options.
- **Document Loader Page**: Allows users to upload, manage, and analyze up to two documents at a time. It provides functionalities for file management and displays the content of uploaded files.
- **LLM Query Page**: A new addition that enables users to query the LLM using either predefined system prompts or custom prompts. It includes functionalities for prompt management, querying the LLM, saving results, and downloading the results as a CSV file.
- **In-depth Documentation**: Provides users with detailed instructions on how to use the testbench effectively, including setting up database connections, handling documents, configuring LLM parameters, managing document uploads, and querying the LLM.

## How to Use
1. **Login**: Users must first log in with their credentials. The application checks the username and password against stored secrets for authentication.
2. **Navigation**: After successful login, users can navigate through the application using the sidebar. It is recommended to start with the instructions page.
3. **Database Manager**: Users can set up a database connection for storing and managing test data. An in-memory storage option is available but not recommended. This page allows users to choose between using a MySQL database, a CSV file, or Tapio's backend database for result logging. Users can also test, refresh, or close the database connection, and manage database tables.
4. **Document Handling**: The 'Document loader page' allows users to upload and manage up to two documents for conflict analysis. It includes features for file upload, file management, and content display.
5. **LLM Setup**: On the 'LLM setup' page, users must enter the necessary credentials and parameters for accessing and using the LLM.
6. **LLM Querying**: The 'LLM query' page allows users to interact with the LLM using predefined or custom prompts. Users can manage prompts, query the LLM, save results, and download the results as a CSV file.
7. **Logout**: Users can log out at any time, which clears their session data and reruns the application for the next login.

## Important Notes
- The application is designed for research purposes, specifically for the thesis _Generative AI in Analysing Conflicts from Construction Industry Documents_ by Tapio Pulkkinen.
- All variables will reset if the page is refreshed. It is important to complete all required fields for tests to function properly.
- The application provides a short introduction and detailed instructions for users to ensure a smooth testing experience.

## Technical Requirements
- Users must have access to LLM credentials (e.g., OpenAI API keys) for LLM setup.
- For database management, users may need access to MySQL credentials or opt for CSV storage based on their preference.


