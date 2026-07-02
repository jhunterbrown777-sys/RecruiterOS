# RecruiterOS

## Mission

RecruiterOS is an AI-powered desktop application that helps job seekers, recruiters, recruiting firms, and HR departments manage the entire recruiting lifecycle.

This is NOT a CRUD application.

This is an AI operating system for recruiting.

---

## Philosophy

Favor:

- Modular architecture
- Readable code
- Small classes
- Clear interfaces
- Dependency injection where appropriate
- Strong typing
- Extensible plugin architecture

Avoid:

- Monolithic files
- Tight coupling
- Duplicate logic
- Global state
- Premature optimization

---

## Architecture

RecruiterOS follows a modular monolith architecture.

Top level modules include:

- kernel
- domain
- services
- automation
- plugins
- gui
- ui
- memory

Each module should be independently maintainable.

---

## UI

Desktop application using PySide6.

The UI should feel similar to:

- VS Code
- Linear
- Notion
- Raycast

Modern.

Minimal.

Fast.

Professional.

Dark mode first.

---

## AI

AI should assist users.

AI should NEVER make irreversible actions automatically.

Human approval should be required before:

- submitting applications
- deleting data
- modifying important profile information

---

## Code Style

- Python 3.14
- Type hints
- Dataclasses when appropriate
- Composition over inheritance
- Small methods
- Docstrings on public APIs

---

## Project Goal

RecruiterOS should eventually become the best AI recruiting platform available for:

- individuals
- recruiters
- recruiting firms
- HR departments

Every design decision should support long-term scalability.