import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.loader.factory_data_loader import FactoryDataLoader
from src.planner.production_planner import ProductionPlanner
from src.utils.logging import log

def main():
    loader = FactoryDataLoader()
    loader.load_all()
    
    planner = ProductionPlanner()
    
    # Get all orders and machines
    orders = list(loader.orders.values())
    machines = list(loader.machines.values())
    
    log.info("Running planner...")
    candidates = planner.plan(orders, machines)
    
    log.info("\n--- Generated Candidates ---")
    for c in candidates:
        print(c)
        
    if not candidates:
        log.error("No candidates generated!")
        sys.exit(1)
        
    log.success("Planner verification complete.")

if __name__ == "__main__":
    main()
