from collections import defaultdict
from src.entities.order import Order
from src.entities.recipe import Recipe
from src.entities.machine import Machine
from src.entities.production_task_candidate import ProductionTaskCandidate
from src.utils.logging import log

class ProductionPlanner:
    """
    Planner that groups orders by recipe and finds suitable machine candidates.
    """

    def group_orders_by_recipe(self, orders: list[Order]) -> dict[Recipe, float]:
        """
        Aggregates quantities from all orders for each recipe.
        """
        grouped = defaultdict(float)
        for order in orders:
            for item in order.items:
                grouped[item.recipe] += item.quantity
        return dict(grouped)

    def create_candidates(
        self, 
        grouped_orders: dict[Recipe, float], 
        machines: list[Machine]
    ) -> list[ProductionTaskCandidate]:
        """
        Generates candidates for each recipe-machine combination.
        """
        candidates = []
        
        for recipe, quantity in grouped_orders.items():
            machines_that_can_produce = 0
            for machine in machines:
                setting = machine.get_setting_for_recipe_from_name(recipe.name)
                if setting:
                    # Machine supports this recipe                    
                    candidate = ProductionTaskCandidate(
                        machine=machine,
                        recipe=recipe,
                        requested_quantity=quantity,                        
                    )
                    candidates.append(candidate)
                    machines_that_can_produce += 1
                    log.trace(f"Created {candidate}")                
            if machines_that_can_produce == 0:
                log.error(f"No machines found to produce '{recipe.name}'")
                    
        return candidates

    def create_candidates(self, orders: list[Order], machines: list[Machine]) -> list[ProductionTaskCandidate]:
        """
        Main entry point: groups orders and creates candidates.
        """
        log.info(f"Planning for {len(orders)} orders and {len(machines)} machines...")
        
        grouped = self.group_orders_by_recipe(orders)
        log.info(f"Grouped into {len(grouped)} unique recipes.")
        
        candidates = self.create_candidates(grouped, machines)
        log.success(f"Generated {len(candidates)} candidates.")
        
        return candidates
