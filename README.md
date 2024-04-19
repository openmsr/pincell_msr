# Pincell MSR depletion
This is a slightly modified version of the [OpenMC pincell depletion](https://github.com/openmc-dev/openmc/tree/main/examples/pincell_depletion) example, aimed to show some recent depletion capabilities developed primarily for Molten Salt Reactor (MSR) simulations.

## Functionalities:

### Transfer Rates
`TransferRates` methodology allows continuous material reprocessing (removal/feed) during a depletion or coupled transport-depletion simulation.
It has been integrated into OpenMC main code from version 0.14.0 and more info can be found on the user manual.    

### Reactivity control
Reactivity control is currently an openmc-dev [open PR](https://github.com/openmc-dev/openmc/pull/2693). It allows to add reactivity controls during a transport-depletion simulation with the aim of keep `keff`equals to 1 as a function of some user defined parameters, such as the geometrical position of a control rod or some batchwise material addition or removal.

### Redox control
Redox control is another [open PR](https://github.com/openmc-dev/openmc/pull/2783) that adds the capability to maintain the redox of the fuel salt constant during a depletion simulation, by continuously adding or removing a user-defined buffer nuclides vector. It makes use of the `TransferRates` implementation to add a further term to the Bateman equation.

For example, UF4 frees 4 atoms of fluorine every time a fission event occurs, which will then bind with fission products with lower oxidation states than uranium, giving rise to an excess of free fluorine atoms and thus increasing the redox potential of the salt.  On the other hand, neutron capture reactions, will likely increase the oxidation state of the transmuting nuclide, thus creating a deficiency of fluorine atoms and reducing the redox potential of the salt.  
Assuming the oxidation states of the nuclides present in the salt are known, the redox can be computed multiplying the number of atoms $N_i$ of each nuclide present in the salt, by their oxidation states $Ox_i$:
```math
\begin{equation}
\sum_i N_i Ox_i
\end{equation}
```

The added term for a generic buffer nuclide can be expressed mathematically  as:
```math
\frac{dN_b(t)}{dt} = \cdots + \frac{1}{Ox_b}\sum_i N_i\left( L_{ii}Ox_i - \sum_j G_{i\rightarrow j } Ox_j\right)
```
where $`Ox_b`$ is the oxidation state of the buffer nuclide, and $`Ox_i`$, $`Ox_j`$ are the oxidation states of the i-th nuclide undergoing a reaction or a decay and of the j-th product nuclide, respectively.
Therefore, the first term in the right hand side represents the losses of the i-th nuclide (i.e. the diagonal terms of the Bateman matrix), and the second term the gains of the j-th nuclides (i.e. the off-diagonal terms of the Bateman matrix).
