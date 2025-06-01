import openmc
import os

os.makedirs("output", exist_ok=True)
os.chdir("output")

##############################################
                # Materials #
##############################################

uo2 = openmc.Material(name="uo2")
uo2.add_nuclide('U235',0.04)
uo2.add_nuclide('U238',0.96)
uo2.add_nuclide('O16',2.0)
uo2.set_density('g/cm3',10.4)
uo2.depletable = True

zirconium = openmc.Material(name="zirconium")
zirconium.add_element('Zr',1.0)
zirconium.set_density('g/cm3',6.55)
zirconium.depletable = False

water = openmc.Material(name="water")
water.add_nuclide('H1',2.0)
water.add_nuclide('O16',1.0)
water.set_density('g/cm3',1.0)
water.add_s_alpha_beta('c_H_in_H2O')

materials = openmc.Materials([uo2, zirconium, water])
materials.export_to_xml()

##############################################
                # Geometry #
##############################################

fuel_outer_radius = openmc.ZCylinder(r=0.4096)
clad_inner_radius = openmc.ZCylinder(r=0.4179)
clad_outer_radius = openmc.ZCylinder(r=0.4750)

fuel_region = -fuel_outer_radius
gap_region = +fuel_outer_radius & -clad_inner_radius
clad_region = +clad_inner_radius & -clad_outer_radius

fuel = openmc.Cell(1,name='fuel')
fuel.fill = uo2
fuel.region = fuel_region

gap = openmc.Cell(name='air gap')
gap.region = gap_region

clad = openmc.Cell(name='clad')
clad.fill = zirconium
clad.region = clad_region

pitch = 1.26
box = openmc.model.RectangularPrism(width=pitch, height=pitch,
                                    boundary_type='reflective')
type(box)

water_region = +clad_outer_radius & -box

moderator = openmc.Cell(name='moderator')
moderator.fill = water
moderator.region = water_region

fuel.temperature = 900
moderator.temperature = 600

root_universe = openmc.Universe(cells=(fuel, gap, clad, moderator))

geometry = openmc.Geometry()
geometry.root_universe = root_universe
geometry.export_to_xml()

##############################################
                # Settings #
##############################################

settings = openmc.Settings()
settings.batches = 100
settings.inactive = 50
settings.particles = 1000
settings.source = openmc.IndependentSource(space=openmc.stats.Point((0,0,0)))
settings.verbosity = 5

settings.export_to_xml()

##############################################
                # Depletion #
##############################################

from openmc.deplete import Operator, PredictorIntegrator
import openmc

openmc.config['chain_file'] = '/home/natem/Projects/openmc-pwr-burnup/chain_endfb71_pwr.xml'

model = openmc.model.Model(geometry, materials, settings)

from config import power

operator = Operator(model)
timesteps = [24*60*60*2] * 5
integrator = PredictorIntegrator(operator, timesteps, power=power)
integrator.integrate()

##############################################
                # Tallies #
##############################################

cell_filter = openmc.CellFilter(fuel)

tally = openmc.Tally(1)
tally.filters = [cell_filter]
tally.nuclides = ['U235']
tally.scores = ['total', 'fission', 'absorption', '(n,gamma)']

tallies = openmc.Tallies([tally])
tallies.export_to_xml()

##############################################
                # Run #
##############################################

openmc.run()
