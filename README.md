# Tiny Compiler + IDE

## Overview

Academic project (Dec 2024) consisting of a small compiler for the *Tiny* language implemented in Python, coupled with a basic IDE for writing and executing programs.
The project focuses on core compilation stages: lexical, syntactic, and semantic analysis, along with simple error reporting.

## Requirements
- Python 3.11
- Java 21 (OpenJDK, LTS)

## Features

* Lexer and parser for a Tiny-like language
* Basic semantic validation
* Execution/testing through a simple IDE interface
* Error handling during compilation stages

## Architecture

The system is implemented as a single Python application where the compiler and IDE are tightly coupled.
Core components include:

* Lexer (tokenization)
* Parser (syntax analysis)
* Semantic checks
* Basic GUI layer for interaction and execution

## Limitations

* Strong coupling between IDE and compiler components
* Mixed programming paradigms (OOP + functional) without strict boundaries
* Reliance on Java-based elements for some UI components
* Not designed for scalability or production use

## Project Status

Archived – this project is no longer actively maintained.
It was developed as a learning exercise during college.

## Reflection

* The compiler logic should be decoupled from the IDE
* A clearer architecture and module separation should be defined upfront
* Cross-language dependencies (Java + Python) should be avoided
* Improved structure and testing would increase maintainability

## Setup & Execution

### 1. Create virtual environment

`python3 -m venv .venv`

### 2. Activate virtual environment

**Linux & MacOS**
`source .venv/bin/activate`

**Windows (CMD)**
`.\.venv\Scripts\activate`

### 3. Install dependencies

`pip install -r requirements.txt`

### 4. Run the application

`python ide.py`

### 5. Deactivate environment

`deactivate`
