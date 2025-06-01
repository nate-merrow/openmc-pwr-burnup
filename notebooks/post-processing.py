import os

os.makedirs("visual_output", exist_ok=True)

##############################################
            # Post-Processing #
##############################################

import matplotlib
matplotlib.use('Agg')  
import numpy as np
import openmc.deplete
from openmc.deplete import Results
import matplotlib.pyplot as plt
from config import power, initial_hm_mass_kg, fuel_volume

results = Results("output/depletion_results.h5")

times = results.get_depletion_time()
days = [t / 86400 for t in times]

burnup = [power * t / 86400 / initial_hm_mass_kg for t in times]
burnup = np.insert(burnup, 0, 0.0)

########## Nuclide Tracking ##########

os.chdir("visual_output")

plt.figure()

nuclides = ['U235', 'U238', 'Pu239', 'Pu240', 'Pu241', 'Am241', 'Np239', 'Xe135', 'Sm149', 'I135']

for nuclide in nuclides:
    _, atoms = results.get_atoms('1', nuclide)
    atom_fractions = atoms / fuel_volume
    plt.plot(burnup, atom_fractions, label=nuclide)

plt.xlabel("Burnup [MWd/kgU]")
plt.ylabel("Atom Fractions")
plt.yscale("log")
plt.title("Isotopic Evolution")
plt.legend()
plt.grid()
plt.savefig("atom_fractions_fixed.png")

########## K-eff Over Time ##########

_, k_values = results.get_keff()
k_mean = k_values[:, 0]

plt.figure()
plt.plot(days, k_mean[1:], 'o')
plt.xlabel("Time [days]")
plt.ylabel("k-effective")
plt.title("k-eff Over Time")
plt.grid()
plt.savefig("k_effective.png")

plt.figure()
plt.plot(burnup, k_mean, 'o')
plt.xlabel("Burnup [MWd/kgU]")
plt.ylabel("k-effective")
plt.savefig("k_eff_vs_burnup.png")

########## Decay Heat and Activity ##########

import openmc

uo2 = openmc.Material(1,name="uo2")
uo2.add_nuclide('U235', 0.04)
uo2.add_nuclide('U238', 0.96)
uo2.add_nuclide('O16', 2.0)
uo2.set_density('g/cm3', 10.4)
uo2.depletable = True

openmc.config['chain_file'] = '/home/natem/Projects/openmc-pwr-burnup/chain_endfb71_pwr.xml'

decay_heat_mean = results.get_decay_heat('1')[1]

plt.figure()
plt.plot(burnup, decay_heat_mean, 'o')
plt.xlabel("Burnup [MWd/kgU]")
plt.ylabel("Decay Heat [W]")
plt.title("Total Decay Heat vs Burnup")
plt.grid()
plt.savefig("decay_heat.png")

activity_mean = results.get_activity('1')[1]

plt.figure()
plt.plot(burnup, activity_mean, 'o')
plt.xlabel("Burnup [MWd/kgU]")
plt.ylabel("Total Activity [Bq]")
plt.title("Activity vs Burnup")
plt.grid()
plt.savefig("activity.png")


