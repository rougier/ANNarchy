from ANNarchy4 import *
from pylab import plot, show

setup()

# Define the neurons
Izhikevitch = Neuron(
    baseline = -65.0,
    a = Variable(init=0.02),
    b = Variable(init=0.2),
    c = Variable(init=-65.0),
    d = Variable(init=2.0),
    noise = Variable(eq=Uniform(0,1)),
    I = Variable(init=0.0, eq="I = noise + sum(exc) - sum(inh)"),
    u = Variable(init=-65.*0.2, eq="u = a * (b*mp - u)"), # init should be b*baseline
    mp = SpikeVariable(eq="dmp/dt = 0.04 * mp * mp + 5*mp + 140 -u +I", threshold=30.0, init=-65, reset=['mp = c', 'u = u+d']),
    order = ['I', 'mp', 'u']
)

# Create the populations
Excitatory = Population(name="Excitatory", geometry=(40, 20), neuron=Izhikevitch)
Excitatory.a = 0.02
Excitatory.b = 0.2
Excitatory.c = Uniform(-65., -50.).get_values((40, 20))
Excitatory.d = Uniform( 2., 8.).get_values((40, 20))
Excitatory.noise = Uniform(0.,5.)

Inhibitory = Population(name="Inhibitory", geometry=(20, 10), neuron=Izhikevitch)
Inhibitory.a = Uniform(0.02, 1.).get_values((20, 10))
Inhibitory.b = Uniform(0.2, 0.25).get_values((20, 10))
Inhibitory.c = -65.
Inhibitory.d = 2.0
Inhibitory.noise = 2.0

#
## Connect the populations
exc_exc = Projection(
                     pre=Excitatory, 
                     post=Excitatory, 
                     target='exc',
                     connector=Connector('All2All', weights=Uniform(0.0, 0.5))
                    )
exc_inh = Projection(pre=Excitatory, 
                     post=Inhibitory, 
                     target='exc',
                     connector=Connector('All2All', weights=Uniform(0.0, 0.5))
                    )
inh_exc = Projection(pre=Inhibitory, 
                     post=Excitatory, 
                     target='inh',
                     connector=Connector('All2All', weights= Uniform(0.0, 1.0))
                    )
inh_inh = Projection(
                     pre=Inhibitory, 
                     post=Inhibitory, 
                     target='inh',
                     connector=Connector('All2All', weights=Uniform(0.0, 1.0))
                    )

# Compile
compile()

if __name__ == '__main__':
    # Run the simulation
    to_record = [
        { 'pop': Excitatory, 'var': 'u' }, 
        { 'pop': Excitatory, 'var': 'mp' }
    ]
    
    record( to_record )
    simulate(200)
    data = get_record( to_record )
    
    neur_1 = data['Excitatory']['mp']['data'][1,1,:]
    neur_2 = data['Excitatory']['mp']['data'][10,1,:]
    
    plot( neur_1 )
    plot( neur_2 )
    
    show()
    
    raw_input('Press a key to continue ...')