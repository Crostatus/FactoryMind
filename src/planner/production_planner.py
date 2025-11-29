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

    def _create_candidates(
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
        
        candidates = self._create_candidates(grouped, machines)
        if candidates.count == 0:
            log.warn("No candidates generated")
        else: 
            log.success(f"Generated {len(candidates)} candidates")
        
        return candidates

    def optimize_assignment(self, candidates: list[ProductionTaskCandidate]) -> list[ProductionTaskCandidate]:
        """
        Optimizes the assignment of recipes to machines using MILP.
        Each recipe is assigned to exactly one machine (no splitting).
        Minimizes makespan (total time to complete all work).
        """
        if not candidates:
            return []

        import pulp

        # Group candidates by recipe
        candidates_by_recipe = defaultdict(list)
        for c in candidates:
            candidates_by_recipe[c.recipe.name].append(c)
        
        # Get unique machines
        machines = {c.machine.name for c in candidates}
        recipes = list(candidates_by_recipe.keys())
        
        # Create a lookup: candidate_map[recipe_name][machine_name] = candidate
        candidate_map = {}
        for recipe_name, recipe_candidates in candidates_by_recipe.items():
            candidate_map[recipe_name] = {c.machine.name: c for c in recipe_candidates}

        # Define the LP Problem
        prob = pulp.LpProblem("Recipe_Assignment", pulp.LpMinimize)

        # Decision variables: x[recipe][machine] = 1 if recipe is assigned to machine
        x = {}
        for recipe_name in recipes:
            x[recipe_name] = {}
            for machine_name in candidate_map[recipe_name]:
                x[recipe_name][machine_name] = pulp.LpVariable(
                    f"x_{recipe_name}_{machine_name}", 
                    cat=pulp.LpBinary
                )

        # Makespan variable
        makespan = pulp.LpVariable("Makespan", lowBound=0, cat=pulp.LpContinuous)

        # Objective: Minimize Makespan (primary) + Total Time (secondary)
        # Use epsilon for secondary objective to break ties without affecting primary
        epsilon = 0.0001
        total_time = pulp.lpSum([
            x[recipe_name][machine_name] * candidate_map[recipe_name][machine_name].estimated_time
            for recipe_name in recipes
            for machine_name in candidate_map[recipe_name]
        ])
        prob += makespan + epsilon * total_time

        # Constraint 1: Each recipe must be assigned to exactly one machine
        for recipe_name in recipes:
            prob += pulp.lpSum([
                x[recipe_name][machine_name] 
                for machine_name in x[recipe_name]
            ]) == 1, f"Recipe_{recipe_name}_Assignment"

        # Constraint 2: Makespan must be >= total time of each machine
        for machine_name in machines:
            machine_time_terms = []
            for recipe_name in recipes:
                if machine_name in x[recipe_name]:
                    cand = candidate_map[recipe_name][machine_name]
                    machine_time_terms.append(x[recipe_name][machine_name] * cand.estimated_time)
            
            if machine_time_terms:
                prob += pulp.lpSum(machine_time_terms) <= makespan, f"Machine_{machine_name}_Time"

        # Solve
        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        status = pulp.LpStatus[prob.status]
        log.info(f"Optimization Status: {status}")
        
        if status != "Optimal":
            log.warn("Could not find optimal solution. Returning best candidates.")
            return [min(recipe_candidates, key=lambda c: c.estimated_time) 
                    for recipe_candidates in candidates_by_recipe.values()]

        # Extract results
        selected_candidates = []
        for recipe_name in recipes:
            for machine_name in x[recipe_name]:
                if pulp.value(x[recipe_name][machine_name]) == 1:
                    cand = candidate_map[recipe_name][machine_name]
                    selected_candidates.append(cand)
                    log.info(f"Assigned '{recipe_name}' to {machine_name} (Time: {cand.estimated_time:.2f}s)")
                    break

        log.info(f"Optimized Makespan: {pulp.value(makespan):.2f}s")
        return selected_candidates
