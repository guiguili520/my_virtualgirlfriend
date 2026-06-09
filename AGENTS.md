# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

Virtual AI Girlfriend (虚拟AI女友) - A complete system for generating anime-style girlfriend chat datasets, training conversational AI models, and providing a web chat interface. The project focuses on maintaining a consistent "温柔体贴、俏皮可爱" (gentle, playful, cute) persona.

## Common Commands

### Dataset Generation
```bash
# Generate 500 entries (default)
python scripts/generate_dataset.py

# Generate with custom size
python scripts/generate_dataset.py --dataset-size 1000

# View all options
python scripts/generate_dataset.py --help
```

### Web Application
```bash
# Start web chat interface (port 5555)
python web/app.py
# Or use the shell script
./start_web.sh
```

### Testing
```bash
# Run all tests with pytest
pytest tests/ -v

# Run specific test files
python tests/test_acceptance_criteria.py
python tests/test_variation_engine.py
python tests/test_inference_pipeline.py
python tests/test_mcp_client.py
python tests/test_mcp_config.py
python tests/test_enhance_modules.py
python tests/test_web_app.py
```

### Model Training
```bash
# Full fine-tuning
python scripts/fine_tune.py

# LoRA fine-tuning
python scripts/lora_train.py
```

### Inference Pipeline Demo
```bash
python demo_inference_pipeline.py
```

## Architecture

### Core Module Structure

```
src/
├── scenarios.py          # 71 dialogue scenarios with 18 categories (SCENARIO_CATALOG)
├── variation_engine.py   # Generates 8-10 style variants per response
├── generator.py          # GirlfriendDatasetGenerator - dataset generation logic
├── config.py             # Global configuration (paths, model settings, enhancement config)
├── inference/
│   └── pipeline.py       # InferencePipeline - main chat inference engine
├── enhance/              # Enhancement modules for inference
│   ├── ranker.py         # Result ranking by relevance
│   ├── deduplicator.py   # Exact + similarity-based deduplication
│   ├── summarizer.py     # Context summarization
│   └── persona_helper.py # Persona validation and emoji injection
└── mcp/                  # Multi-service Content Provider
    ├── config_parser.py  # MCP configuration parser
    └── mcp_client.py     # MCPClient - external service integration
```

### Data Flow

1. **Dataset Generation**: `scenarios.py` → `variation_engine.py` → `generator.py` → JSON output
2. **Inference Pipeline**: User input → Decision (enhance?) → Enhancement (search/MCP) → Model → Persona processing → Response
3. **Web Chat**: Flask app (`web/app.py`) → Inference pipeline → JSON API response

### Key Classes

- **Scenario**: Defines dialogue scenarios with `instruction`, `input`, `response_templates`, `category`, `tags`
- **GirlfriendDatasetGenerator**: Three generation modes - `deterministic`, `random`, `balanced`
- **InferencePipeline**: Main inference entry point via `run_chat(input_text, history, opts)`
- **MCPClient**: External knowledge integration (weather, news, etc.) via `fetch(domain, query)`

### MCP Configuration

MCP services are configured in `mcp.json` at project root:
```json
{
  "mcp": {
    "enabled": true,
    "services": [
      {
        "name": "service_name",
        "endpoint": "https://...",
        "domains": ["weather", "news"],
        "authentication": { "type": "api_key", "key": "ENV_VAR" }
      }
    ]
  }
}
```

## Quality Control Pipeline

The dataset generation includes 5-step QC:
1. Emoji validation (auto-inject if missing)
2. Length validation (15-200 chars)
3. Exact deduplication
4. Similarity deduplication (threshold 0.90)
5. Persona validation (positive words, tone consistency)

## Persona Guidelines

All generated responses must maintain:
- **温柔体贴** (gentle/caring): Show concern for health and emotions
- **俏皮可爱** (playful/cute): Use particles like 呀、啦、呢、哦
- **阳光开朗** (sunny/cheerful): Positive, encouraging tone
- 98%+ emoji coverage in responses

## Key Configuration (src/config.py)

- `PROJECT_ROOT`, `DATA_DIR`, `MODELS_DIR`: Path configuration
- `DEFAULT_SIMILARITY_THRESHOLD = 0.90`: Deduplication threshold
- `PERSONA_EMOJI_PROBABILITY = 0.8`: Emoji injection rate
- `ENHANCEMENT_MIN_QUERY_LENGTH = 4`: Trigger length for enhancement
- `ENHANCEMENT_KEYWORDS`: List of words that trigger search/MCP enhancement

## Output Format

Generated datasets follow the instruction-tuning format:
```json
{
  "instruction": "场景描述",
  "input": "用户输入（可为空）",
  "output": "女友的回复（包含emoji）"
}
```
