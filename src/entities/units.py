from enum import Enum

class Unit(Enum):
    GRAM = "g"
    KILOGRAM = "kg"
    LITER = "L"
    MILLILITER = "mL"
    PIECE = "piece"
    SECONDS = "s"
    KILOWATT = "kW"
    EURO = "€"    
    PERCENT = "%"
    HOUR = "h"
    
    def __str__(self):
        """Human-readable representation (so print(Unit.KILOGRAM) -> 'kg')."""
        return self.value

formated_two_decimals = [Unit.GRAM, Unit.KILOGRAM, Unit.LITER, Unit.KILOWATT, Unit.EURO, Unit.PERCENT]
formatted_no_decimals = [Unit.PIECE, Unit.SECONDS, Unit.MILLILITER]
    
def str_quant(quantity: float, unit: Unit) -> str:
    """Formats a quantity with its unit for display purposes."""
    if(unit in formated_two_decimals):
        return f"{quantity:.2f} {unit.value}"
    if(unit in formatted_no_decimals):
        return f"{int(quantity)} {unit.value}{unit == Unit.PIECE and 's' or ''}"
    return f"{quantity} {unit.value}"    

def str_quant_over_quant(quantity: float, unit: Unit, over: Unit) -> str:
    return f"{str_quant(quantity, unit)}/{over.value}"
    