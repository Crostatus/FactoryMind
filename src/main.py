import sys
import os
import argparse

# Add project root to path
sys.path.append(os.getcwd())

from src.loader.factory_data_loader import FactoryDataLoader
from src.generator.factory_data_generator import FactoryDataGenerator
from src.planner.production_planner import ProductionPlanner
from src.utils.logging import log
from src.entities.production_task_candidate import ProductionTaskCandidate
from src.entities.units import str_quant

def print_candidates_formatted(candidates: list[ProductionTaskCandidate]):
    """
    Stampa i candidati in modo formattato con:
    - Nome macchina
    - Lista di ricette con quantità e tempo in secondi
    - Consumo energetico totale in KWh
    """
    from collections import defaultdict
    
    # Raggruppa per macchina
    candidates_by_machine = defaultdict(list)
    for candidate in candidates:
        candidates_by_machine[candidate.machine.name].append(candidate)
    
    print("\n" + "="*80)
    print("PRODUCTION PLANNING".center(80))
    print("="*80 + "\n")
    
    for machine_name, machine_candidates in sorted(candidates_by_machine.items()):
        print(f"MACHINE: {machine_name}")
        print("-" * 80)
        
        for candidate in machine_candidates:
            quantity_str = str_quant(candidate.requested_quantity, candidate.recipe.output_unit)
            print(f"    RECIPE: {candidate.recipe.name}")
            print(f"     - Quantity: {quantity_str}")
            print(f"     - Time: {candidate.estimated_time:.2f} seconds ({candidate.estimated_time/60:.2f} minutes)")
            print(f"     - Energy: {candidate.total_energy_consumption:.4f} KWh")
            print()
        
    print("="*80)
    
    # Calculate total energy and time metrics
    total_energy = sum(c.total_energy_consumption for c in candidates)
    
    # Calculate time per machine (machines work in parallel)
    machine_times = {}
    for candidate in candidates:
        if candidate.machine.name not in machine_times:
            machine_times[candidate.machine.name] = 0
        machine_times[candidate.machine.name] += candidate.estimated_time
    
    # Total work time = sum of all machine times (total machine hours)
    total_work_time = sum(machine_times.values())
    
    # Makespan = max machine time (actual calendar time needed)
    makespan = max(machine_times.values()) if machine_times else 0
    
    print(f"TOTAL ENERGY CONSUMPTION: {total_energy:.4f} KWh")
    print(f"TOTAL WORK TIME (all machines): {total_work_time:.2f} seconds ({total_work_time/60:.2f} minutes)")
    print(f"MAKESPAN (with machines working in parallel): {makespan:.2f} seconds ({makespan/60:.2f} minutes)")
    print("="*80 + "\n")

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
    parser.add_argument(
        '--orders',
        type=int,
        default=None,
        help='Number of orders to generate (default: random 1-3)'
    )
    parser.add_argument(
        '--min-quantity',
        type=float,
        default=None,
        help='Minimum quantity for each recipe in orders (default: 50 for pieces, 5.0 for kg/L)'
    )
    
    args = parser.parse_args()
    
    # Determine data directory
    if args.generate:
        log.info("Generation mode enabled")
        generator = FactoryDataGenerator()
        generator.generate_and_save_all(
            num_materials=args.materials,
            num_recipes=args.recipes,
            num_machines=args.machines,
            num_orders=args.orders,
            min_order_quantity=args.min_quantity
        )
        data_dir = "src/data/generated"        
    else:
        data_dir = "src/data"
    
    log.info(f"Using data from: {data_dir}\n")
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
    
        
    print_candidates_formatted(candidates)

if __name__ == "__main__":
    main()
