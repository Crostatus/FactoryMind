import sys
import os
import argparse

# Add project root to path
sys.path.append(os.getcwd())

from src.loader.factory_data_loader import FactoryDataLoader
from src.generator.factory_data_generator import FactoryDataGenerator
from src.planner.production_planner import ProductionPlanner
from src.utils.logging import log

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Factory Production Planner')
    parser.add_argument(
        '-g', '--generate',
        action='store_true',
        help='Generate random data before running the planner'
    )
    parser.add_argument(
        '--materials',
        type=int,
        default=None,
        help='Number of materials to generate (default: random 5-15)'
    )
    parser.add_argument(
        '--recipes',
        type=int,
        default=None,
        help='Number of recipes to generate (default: random 3-10)'
    )
    parser.add_argument(
        '--machines',
        type=int,
        default=None,
        help='Number of machines to generate (default: random 2-5)'
    )
    
    args = parser.parse_args()
    
    # Determine data directory
    if args.generate:
        log.info("Generation mode enabled - generating random data...")
        generator = FactoryDataGenerator()
        generator.generate_and_save_all(
            num_materials=args.materials,
            num_recipes=args.recipes,
            num_machines=args.machines
        )
        data_dir = "src/data/generated"
        log.info(f"Using generated data from: {data_dir}\n")
    else:
        data_dir = "src/data"
        log.info(f"Using default data from: {data_dir}\n")
    
    # Load data
    loader = FactoryDataLoader(data_dir=data_dir)
    loader.load_all()
    
    planner = ProductionPlanner()
    
    # Get all orders and machines
    orders = list(loader.orders.values())
    machines = list(loader.machines.values())
    
    log.info("Running planner...")
    candidates = planner.create_candidates(orders, machines)
    
    log.info("Optimizing recipe assignment...")
    candidates = planner.optimize_assignment(candidates)
    
    if not candidates:
        log.error("No candidates generated!")
        sys.exit(1)
        
    log.success("Planner execution complete.")

if __name__ == "__main__":
    main()
