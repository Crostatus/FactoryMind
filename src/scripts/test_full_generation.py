"""
Test script for full data generation and saving
"""
from src.generator.factory_data_generator import FactoryDataGenerator

def main():
    # Create generator
    generator = FactoryDataGenerator()
    
    # Generate and save all data
    summary = generator.generate_and_save_all(
        num_materials=12,
        num_recipes=8,
        num_machines=4
    )
    
    print("\n" + "="*60)
    print("GENERATION SUMMARY")
    print("="*60)
    print(f"Output directory: {summary['output_dir']}")
    print(f"\nGenerated:")
    print(f"  - {summary['materials']} materials")
    print(f"  - {summary['recipes']} recipes")
    print(f"  - {summary['machines']} machines")
    print(f"  - {summary['settings']} machine recipe settings")

if __name__ == "__main__":
    main()
