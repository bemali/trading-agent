# Trading Agent System Architecture

This diagram illustrates the architecture and workflow of the Trading Agent system.

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'primaryColor': '#f0f8ff', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#fff0f0'}}}%%
graph TD
    User[User Input] -->|Question| Entry[Entry Point]
    Entry -->|Initialize| Judge[Judge Agent]
    Judge -->|Evaluate| Check{Reached Verdict?}
    Check -->|No| Research[Research Agent]
    Check -->|Yes| End[Final Verdict & Summary]
    Research -->|Response| CheckRes{Tool Needed?}
    CheckRes -->|Yes| Tools[Tool Node]
    CheckRes -->|No| Judge
    Tools -->|Results| Research
    
    subgraph "Agent Workflow Details"
    Judge -->|Instructions| Research
    Research -->|Findings| Judge
    Judge -->|Analysis| End
    end
    
    subgraph "Data Flow"
    User --> UserProfiles[User Profiles]
    UserProfiles -->|Context| Entry
    End -->|Update| UserProfiles
    end
    
    subgraph "Tools Available"
    Tools --> WebSearch[Web Search]
    WebSearch --> URLs[URL Collection]
    URLs --> ContentParsing[Content Parsing]
    ContentParsing --> Research
    end
    
    classDef agents fill:#d4f1f9,stroke:#05728f,stroke-width:2px;
    classDef flows fill:#ffe6cc,stroke:#d79b00,stroke-width:1px;
    classDef tools fill:#d5e8d4,stroke:#82b366,stroke-width:1px;
    classDef endpoints fill:#e1d5e7,stroke:#9673a6,stroke-width:2px;
    
    class Judge,Research agents;
    class User,Entry,End endpoints;
    class Tools,WebSearch,URLs,ContentParsing tools;
    class UserProfiles,Check,CheckRes flows;
```

## Component Descriptions

### Agents
- **Judge Agent**: Orchestrates the workflow, evaluates research, and provides final verdicts
- **Research Agent**: Performs web searches and information gathering based on judge instructions

### Tools
- **Web Search**: Searches the web using DuckDuckGo search API
- **URL Collection**: Gathers relevant URLs from search results
- **Content Parsing**: Extracts and processes text content from web pages

### Data Flow
- User questions are evaluated by the Judge Agent
- Research Agent gathers information using tools when needed
- Judge Agent makes the final decision when sufficient information is available
- User profiles store conversation history for context in future interactions
