from src.loader.factory_data_loader import FactoryDataLoader

if __name__ == "__main__":
    print('ciao a tutti merde')
    loader = FactoryDataLoader()
    loader.load_all()

    print(loader.summary())
    print()

    for machine in loader.machines.values():
        print(machine.describe())
        print()
