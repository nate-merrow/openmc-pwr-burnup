import math
from openmc.data import atomic_mass

AVOGADRO = 6.02214076e23 

fuel_radius = 0.4096  
fuel_height = 100.0   
fuel_volume = math.pi * fuel_radius**2 * fuel_height

density_U235 = 0.045
density_U238 = 2.2

mass_U235 = density_U235 * fuel_volume 
mass_U238 = density_U238 * fuel_volume 

initial_hm_mass_kg = (mass_U235 + mass_U238) / 1000 
power_density = 37

power = power_density * fuel_volume  

if __name__ == "__main__":
    print(f"Fuel volume: {fuel_volume:.2f} cm3")
    print(f"Initial heavy metal mass: {initial_hm_mass_kg:.3f} kg")
    print(f"Total power: {power:.2f} W")
