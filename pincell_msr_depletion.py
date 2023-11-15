from math import pi
import openmc
import openmc.deplete

# Instantiate some Materials and register the appropriate Nuclides
uo2 = openmc.Material(name='UO2')
uo2.set_density('g/cm3', 10.29769)
uo2.add_element('U', 1., enrichment=2.4)
uo2.add_element('O', 2.)
#uo2.temperature = 293

helium = openmc.Material(name='Helium for gap')
helium.set_density('g/cm3', 0.001598)
helium.add_element('He', 2.4044e-4)

zircaloy = openmc.Material(name='Zircaloy 4')
zircaloy.set_density('g/cm3', 6.55)
zircaloy.add_element('Sn', 0.014, 'wo')
zircaloy.add_element('Fe', 0.00165, 'wo')
zircaloy.add_element('Cr', 0.001, 'wo')
zircaloy.add_element('Zr', 0.98335, 'wo')

borated_water = openmc.Material(name='Borated water')
borated_water.set_density('g/cm3', 0.740582)
borated_water.add_element('B', 4.0e-5)
borated_water.add_element('H', 5.0e-2)
borated_water.add_element('O', 2.4e-2)
borated_water.add_s_alpha_beta('c_H_in_H2O')
#borated_water.depletable = True
#borated_water.volume=22
#borated_water.temperature=293

# Define overall material
material = openmc.Materials([uo2, helium, zircaloy, borated_water])

# Define surfaces
width = 1.25984
height = 200
fuel_or = openmc.ZCylinder(r=0.39218, name='Fuel OR')
clad_ir = openmc.ZCylinder(r=0.40005, name='Clad IR')
clad_or = openmc.ZCylinder(r=0.45720, name='Clad OR')
wat_or = openmc.ZCylinder(r=width/2, name='H2O OR', boundary_type='reflective')
interface = openmc.ZPlane(z0=-59, name='IF')
z_top = openmc.ZPlane(z0=height/2, name='Pin TOP', boundary_type='vacuum')
z_bot = openmc.ZPlane(z0=-height/2, name='Pin BOT', boundary_type='vacuum')

# Define cells
fuel = openmc.Cell(fill=uo2, region=-fuel_or & -z_top & +z_bot)
gap = openmc.Cell(fill=helium, region=+fuel_or & -clad_ir & -z_top & +z_bot)
clad = openmc.Cell(fill=zircaloy, region=+clad_ir & -clad_or & -z_top & +z_bot)
water = openmc.Cell(fill=borated_water, region=+clad_or & -interface )
gas = openmc.Cell(fill=helium, region=+clad_or & +interface)
msr_uni = openmc.Universe(cells=(water, gas))
msr = openmc.Cell(name="MSR", fill=msr_uni, region=-wat_or & -z_top & +z_bot)
# Define overall geometry
geometry = openmc.Geometry([fuel, gap, clad, msr])

# Set material volume for depletion.
uo2.volume = pi * fuel_or.r**2 * height

# Instantiate a Settings object, set all runtime parameters, and export to XML
settings = openmc.Settings()
settings.batches = 30
settings.inactive = 10
settings.particles = 20000

# Create an initial uniform spatial source distribution over fissionable zones
bounds = [-0.62992, -0.62992, -100, 0.62992, 0.62992, 100]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
settings.source = openmc.source.Source(space=uniform_dist)

#Build the model
model = openmc.Model(geometry=geometry, materials=material, settings=settings)

#Create the depletion "operator"
op = openmc.deplete.CoupledOperator(model)
#Create msr continuous instance

integrator = openmc.deplete.CECMIntegrator(op, [10.0]*3 , 1e5, timestep_units='d')

integrator.add_transfer_rate('UO2', ['Xe'], 0.1)

# integrator.add_batchwise(msr, 'translation', axis = 2,
#                           density_treatment = 'constant-volume',
#                           bracket = [-4, 4],
#                           bracket_limit = [-100,20],
#                           tol = 0.1)

# integrator.add_batchwise(msr, 'temperature',
#                           bracket = [-50, 50],
#                           bracket_limit = [-1000,1000],
#                           tol = 0.1)

# integrator.add_batchwise(uo2, 'refuel',
#                           mat_vector = {'U238': 0.8, 'U235': 0.2},
#                           density_treatment = 'constant-density',
#                           bracket = [-100,100], #grams
#                           bracket_limit = [-1e3,1e3],
#                           tol = 0.01)
#
# integrator.add_batchwise('dilute', mats_id_or_name = ['UO2'],
#                           mat_vector = {'U238': 0.8, 'U235': 0.2},
#                           bracket = [0.1,0.9], #fraction
#                           bracket_limit = [0.01,0.99], #fraction
#                           tol = 0.01,
#                           restart_level = 0)
#
# integrator.add_batchwise_wrap('2', dilute_interval=5)

integrator.integrate()
