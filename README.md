# README

## Overview

This repository contains the codebase for the prototype developed during my research at Technical University Munich. The prototype integrates Building Information Modeling (BIM) with Large Language Models (LLMs) to enhance information retrieval (IR) processes within BIM frameworks. The code is organized into three main modules: `llm`, `speckle`, and `streamlit`, each serving distinct purposes to streamline the overall functionality.

There are two different prototypes in the repo:
- PandasAI chatbot (page 2): works better, but one has to manually predefine the category to chat with
- LangChain chatbot (page 3 & 4): still in progress, but more powerful. LLM agent which got appended different tools (specifically the BIM IR tool, the others (PDF retriever, ...) are probably not so interesting for you)

## Structure of the Codebase

### 1. `llm` Module
The `llm` module handles functionalities related to large language models and information retrieval. It is divided into:
- **Tools**: Contains various tools necessary for the Langchain agent.
- **Agent Handlers**: Provides classes with static methods to set up agents, manage their output, and handle logs.

### 2. `speckle` Module
The `speckle` module is designed to manage Speckle data. It includes:
- **SpeckleProject Class**: Manages the loading of Speckle models, acquisition of API tokens, and instantiation of the Speckle client.
- **BaseHandler Class**: Interacts with the Base Object and includes essential Speckle parsing functions.

### 3. `streamlit` Module
The `streamlit` module focuses on front-end components and includes:
- **Pages Folder**: Contains the various pages of the Streamlit prototype, with the initial page located in the base folder due to Streamlit's framework requirements.
- **Streamlit Components**: Modularized into different classes to enhance reusability and address Streamlit’s unique caching rules.

## Installation Guide

### Prerequisites
- Python 3.8 or higher
- Virtual Environment (recommended)
- API keys for Speckle, LLM foundation models, and LangSmith

### Setup Instructions
1. **Clone the Repository**
   ```sh
   git clone https://github.com/your-repo.git
   cd your-repo
   ```

2. **Create and Activate a Virtual Environment**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```sh
   pip install -r requirements.txt
   ```

4. **Install Dependencies**
   - Speckle: Set your Speckle API key in the environment variables or a configuration file.
   - LLM Models: Configure your API keys for the chosen LLM foundation models.
   - LangSmith: Ensure the LangSmith API key is correctly specified.

5. **Specify your Speckle project**
   - go to `modules/speckle/projects.py` and specify the Speckle projects URL and name in the `PROJECTS` variable

### Running the Application
To start the Streamlit server and interact with the prototype, use the following command:
   ```sh
   streamlit run path_to_your_main_script.py
   ```

## Usage

### Exploring Data Structure

- Navigate to the first page to explore the data structure of the Speckle format for the project. This page includes:
  - A Speckle BIM viewer embedded as an iFrame.
  - Data tree structure visualization.
  - Manual filtering options for Speckle categories.

### Chatbot Configurations

- **Page 2**: PandasAI chatbot for data queries.
- **Page 3**: LangChain chatbot with different tools (connected to a german buidling regulation, you need to change that)
- **Page 4**: LangChain chatbot with different tools

### Output Handling

The prototype manages various output formats (text, images, tables) using dedicated output classes. The Factory Design Pattern is utilized to ensure the appropriate output class is returned based on the type of output.

### Settings

All settings for the prototype are accessible via the sidebar and can be updated in the backend through settings classes interfacing with the LLM or Speckle modules.

## Contributing

Contributions to this project are welcome. Please follow the standard GitHub flow:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/jjanixx/bim_ir_chat/blob/main/LICENSE) file for more details.

## Contact

For any questions or support, please contact [Janick Hofer](mailto:janick.hofer@tum.de).
