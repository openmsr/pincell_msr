from math import pi
import openmc
import openmc.deplete
import matplotlib.pyplot as plt

import re
import h5py
import numpy as np

# Load geometry from statepoint
statepoint = 'statepoint.100.h5'
with openmc.StatePoint(statepoint) as sp:
    geometry = sp.summary.geometry

# Load previous depletion results
previous_results = openmc.deplete.Results("depletion_results.h5")

# Instantiate a Settings object, set all runtime parameters, and export to XML
settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 1000

# Create an initial uniform spatial source distribution over fissionable zones
bounds = [-0.62992, -0.62992, -100, 0.62992, 0.62992, 100]
uniform_dist = openmc.stats.Box(bounds[:3], bounds[3:], only_fissionable=True)
settings.source = openmc.source.Source(space=uniform_dist)

#Build the model
model = openmc.Model(geometry=geometry, settings=settings)

#Get last level
msr_cell = model.geometry.get_cells_by_name('MSR')[0]
with h5py.File('msr_results.h5','r') as h5:
    last_n = sorted([int(re.split('_',i)[1]) for i in h5.keys()])[-1]
    last_key = '_'.join(['geometry', str(last_n)])
    last_level = np.array(h5.get(last_key)).mean()
    setattr(msr_cell, 'translation', [0,0,last_level])
    print(last_level)

#Create depletion "operator"
chain_file = '/home/lorenzo/ca_depletion_chains/chain_simple.xml'
# Perform simulation using the predictor algorithm
time_steps = [10.0, 10.0]  # days
power = 100000  # W
#Create the depletion "operator"
op = openmc.deplete.CoupledOperator(model, chain_file, previous_results)
#Create msr continuous instance
msr_c = openmc.deplete.msr.MsrContinuous(op, model)
# Set removal rate from UO2 for Xe. Default units is [sec-1]
msr_c.set_removal_rate('UO2 fuel at 2.4% wt enrichment', ['Xe'], 0.1)
#Create msr batchwise geometrical instance
msr_g = openmc.deplete.msr.MsrBatchwiseGeom(op, model, cell_id_or_name = 'MSR',
                                            axis=2, bracket=[-2,2],
                                            bracket_limit=[-100,100],
                                            tol=0.01, target=1.00)
# Pass the msr instance to the integrator object
integrator = openmc.deplete.PredictorIntegrator(op, time_steps, power,
                                                msr_continuous=msr_c,
                                                msr_batchwise=msr_g,
                                                timestep_units='d')
integrator.integrate()
