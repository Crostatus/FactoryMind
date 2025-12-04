# FactoryMind

A Python-based production planning system for optimizing manufacturing operations. The system uses Mixed-Integer Linear Programming  to minimize makespan while respecting machine capabilities, material availability, and operational constraints.

## Features

- **Production Optimization**: MILP-based task assignment to minimize total production time
- **Energy Consumption**: Calculates energy usage based on machine power profiles (idle, loading, production)
- **Realistic Time Modeling**: Accounts for machine working hours, (un)loading time, batch capacities
- **Data Generation**: Built-in random factory data generator for testing and simulation
- **Yield Rate Handling**: Considers production waste and calculates actual quantities needed

## Project Structure

```
project_work/
├── src/
│   ├── data/              # Static production data (materials, recipes, machines, orders)
│   ├── entities/          # Domain models (Machine, Recipe, Order, etc.)
│   ├── generator/         # Random data generator
│   ├── loader/            # Data loading and validation
│   ├── planner/           # Production planning and optimization
│   ├── schemas.py         # Pydantic validation schemas
│   └── main.py            # Entry point
└── README.md
```

## Installation

### Prerequisites

- Python 3.12+
- pip

### Setup

1. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r src/requirements.txt
```

## Usage

### Run with static data

Use data from `src/data/`:

```bash
python3 -m src.main
```

### Generate random data

Generate random factory data and run the planner:

```bash
python3 -m src.main -g
```

Or specify the number of entities to generate:

```bash
python3 -m src.main -g --materials 10 --recipes 5 --machines 3 --orders 2 --min-quantity 200
```

### Command-line Options

- `-g, --generate`: Generate random data before running the planner
- `--materials N`: Number of materials to generate (default: random 5-15)
- `--recipes N`: Number of recipes to generate (default: random 3-10)
- `--machines N`: Number of machines to generate (default: random 2-5)
- `--orders N`: Number of orders to generate (default: random 1-3)
- `--min-quantity X`: Minimum quantity for each recipe in orders (default: 50 for pieces, 5.0 for kg/L)

## Output

The planner produces a production schedule showing:

- **Production assignments**: Which machine produces which recipe
- **Time estimates**: Individual task times and overall makespan
- **Energy consumption**: KWh consumption per task and total
- **Material validation**: Stock availability checks

Example output:
```
PRODUCTION PLANNING
================================================================================

MACHINE: Packaging Unit A
--------------------------------------------------------------------------------
    RECIPE: Butter Biscuits
     - Quantity: 1500 pieces
     - Time: 1068.00 seconds (17.80 minutes)
     - Energy: 2739.6000 KWh

================================================================================
TOTAL ENERGY CONSUMPTION: 2739.6000 KWh
TOTAL WORK TIME (all machines): 1068.00 seconds (17.80 minutes)
MAKESPAN (calendar time): 1068.00 seconds (17.80 minutes)
================================================================================
```

## Key Concepts

- **Makespan**: Total calendar time to complete all production (max of all machine times)
- **Yield Rate**: Percentage of good output vs. raw production (affects material requirements)
- **Batch Capacity**: Maximum quantity a machine can process in one batch
- **Power Profile**: Machine energy consumption at different states (idle, loading, producing)
- **Max Working Hours**: Daily operational limit for each machine

## Dependencies

- `pydantic`: Data validation and settings management
- `pulp`: Linear programming and optimization
- Additional dependencies listed in `src/requirements.txt`
