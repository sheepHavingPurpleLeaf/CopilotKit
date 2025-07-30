# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

CopilotKit is a monorepo containing a React-based AI copilot framework with both JavaScript/TypeScript and Python SDKs. The main codebase is in `CopilotKit/` with numerous example applications in `examples/`.

## Essential Commands

### Development Setup
```bash
# Initial setup (must be in CopilotKit/ directory)
cd CopilotKit
pnpm install
turbo run build

# Development mode (runs all packages)
turbo run dev

# Run specific package in dev mode
turbo run dev --filter="@copilotkit/package-name"
```

### Build and Testing
```bash
# Build all packages
turbo run build

# Clean build (recommended when dependencies change)
pnpm run freshbuild

# Run tests
turbo run test

# Type checking
turbo run check-types

# Linting
turbo run lint

# Format code
pnpm run format
```

### Documentation
```bash
# Generate documentation
pnpm run docs
```

## Architecture Overview

### Core Package Structure
- **`CopilotKit/packages/react-core`** - Core React hooks and providers (`useCopilotChat`, `useCopilotAction`, `useCoAgent`)
- **`CopilotKit/packages/react-ui`** - Pre-built UI components (`CopilotPopup`, `CopilotSidebar`, `CopilotChat`)
- **`CopilotKit/packages/react-textarea`** - AI-powered textarea component with autosuggestions
- **`CopilotKit/packages/runtime`** - Backend runtime for handling LLM integrations and GraphQL API
- **`CopilotKit/packages/runtime-client-gql`** - GraphQL client for communication between frontend and runtime
- **`CopilotKit/packages/sdk-js`** - JavaScript/Node.js SDK for backend agent development
- **`CopilotKit/packages/shared`** - Shared types and utilities across packages

### Python SDK
- **`sdk-python/`** - Python SDK with LangGraph and CrewAI integrations
- **`sdk-python/copilotkit/crewai/`** - CrewAI-specific integrations for multi-agent workflows

### Examples Architecture
Most examples follow this pattern:
- **`ui/`** - Next.js frontend application using CopilotKit React components
- **`agent/` or `agent-py/`** - Backend agent implementation (Python with LangGraph/CrewAI)
- **`agent-js/`** - JavaScript backend agent (when available)

Key example categories:
- **`coagents-*`** - Multi-agent systems with shared state
- **`copilot-*`** - Single-agent copilot implementations
- **`*-crewai-*`** - CrewAI-based examples

## Key Concepts

### Frontend Integration
- **CopilotProvider** - Root context provider for the application
- **useCopilotChat** - Hook for chat functionality with message handling
- **useCopilotAction** - Hook for defining actions the AI can call
- **useCoAgent** - Hook for connecting to backend agents with shared state
- **useCoAgentStateRender** - Hook for rendering agent state as generative UI

### Backend Agents
- **LangGraph agents** - Built using `@copilotkit/runtime` and `sdk-python`
- **CrewAI integration** - Multi-agent workflows using `copilotkit[crewai]` extra
- **Actions** - Functions that agents can call to interact with frontend
- **State management** - Shared state between frontend and backend agents

### Development Tools
- **Turbo** - Build system for the monorepo
- **pnpm workspaces** - Package management and linking
- **TypeScript** - Primary language for frontend packages
- **Python Poetry** - Dependency management for Python SDK

## Development Guidelines

### Working with Examples
1. Examples reference local packages via workspace protocol
2. Always run `turbo run build` from `CopilotKit/` before working with examples
3. Use `turbo run dev` for hot reloading during development

### Testing
- E2E tests are in `examples/e2e/` using Playwright
- Unit tests are co-located with source code in each package
- Run tests after making changes to core packages

### Package Dependencies
- Packages have complex interdependencies managed by Turbo
- Runtime generates GraphQL schema that `runtime-client-gql` depends on
- Always build in dependency order using `turbo run build`

### Python Development
- Use Poetry for dependency management
- LangGraph agents should extend the base agent classes from `copilotkit`
- CrewAI integration available via `copilotkit[crewai]` extra

## Important Files
- **`CopilotKit/turbo.json`** - Build pipeline configuration
- **`CopilotKit/pnpm-workspace.yaml`** - Workspace package definitions
- **`sdk-python/pyproject.toml`** - Python SDK configuration
- **`.cursor/rules/`** - Additional development guidelines and architecture notes