from ANNarchy4 import *
from pylab import show, figure, subplot, legend, close

#
# experiment setup
setup(dt=1)
nb_steps = 300
nb_exc_neurons = 800
nb_exc_neurons = 200

# Define the neurons
Izhikevitch = Neuron(
    I_in = Variable(init=0.0),
    I = Variable(init=0.0, eq = "I = I_in + sum(exc) - sum(inh) + noise"),
    noise = Variable(eq=Uniform(0.0,5.0)),
    a = 0.02,
    b = 0.2,
    c = -65.0,
    d = 6.0,
    u = Variable(init=-65.*0.2, eq="du/dt = a * (b*v - u)"), # init should be b*baseline
    v = SpikeVariable(eq="dv/dt = 0.04 * v * v + 5*v + 140 -u + I", threshold= 30.0, init=-65.0, reset=['v = c', 'u = u+d']),
    order = ['I', 'v','u']
)

Simple = Synapse(
    psp = Variable(init=0, eq = "psp = exp(-(t - t_spike))*value")  
)

Excitatory = Population(name='Excitory', geometry=(nb_exc_neurons), neuron=Izhikevitch)
Inhibitory = Population(name='Inhibitory', geometry=(nb_exc_neurons), neuron=Izhikevitch)
Inhibitory.noise = Variable(eq=Uniform(0.0,2.0))
Inhibitory.d = 2.0

exc_exc = Projection(
    pre=Excitatory, 
    post=Excitatory, 
    target='exc',
    synapse = Simple,
    connector=Connector('All2All', weights=Uniform(0,0.5))
)
 
exc_inh = Projection(
    pre=Excitatory, 
    post=Inhibitory, 
    target='exc',
    synapse = Simple,
    connector=Connector('All2All', weights=Uniform(0,0.5))
)

inh_exc = Projection(
    pre=Inhibitory, 
    post=Excitatory, 
    target='inh',
    synapse = Simple,
    connector=Connector('All2All', weights= Uniform(-1.0,0.0))
)

inh_inh = Projection(
    pre=Inhibitory, 
    post=Inhibitory, 
    target='inh',
    synapse = Simple,
    connector=Connector('All2All', weights=Uniform(-1.0,0.0))
)

# Compile
compile()

def plot(population, data):
    """
    Plot the recorded data of one population.
    """
    input =  data[population.name]['I']['data']
    neur_v =  data[population.name]['v']['data']
    neur_u =  data[population.name]['u']['data']    
    
    nb_neurons = population.size
    
    X = np.arange(nb_steps)
    spikes = np.zeros((nb_neurons, nb_steps))
    timing = population.cyInstance.get_spike_timings()
        
    #
    # reformat data for plot  
    if timing.shape == (nb_neurons,):  
        for i in xrange(nb_neurons):
            if len(timing[i])>1:
                neur_v[ i, timing[i] ] = 30
                spikes[ i, timing[i] ] = 1
        
    rest_pot = np.ones((nb_steps,1)) * -65.0
    threshold = np.ones((nb_steps,1)) * 30.0
        
    X = np.arange(nb_steps)
    for i in range(1):
        fig = figure()
        fig.suptitle('Population '+population.name)
        
        ax = subplot(311)
        ax.plot( neur_v[i,:], label = "membrane potential")
        ax.plot( neur_u[i,:], label = "membrane recovery")
        ax.plot( rest_pot, label = "resting potential")
        ax.plot( threshold, label = "threshold")
        ax.legend(loc=2)
        ax.set_ylim([-70,40])
        
        ax = subplot(312)
        ax.plot( input[i,:] )
        ax.set_ylim([-70,40])
        
        ax = subplot(313)
        ax.bar( X, spikes[i,:] )
        ax.set_xlim([0,nb_steps])

    fig = figure()
    fig.suptitle('Population '+population.name)
    
    ax = subplot(111)
    ax.imshow( spikes, cmap='hot' )
    ax.set_xlim([0,nb_steps])
        
if __name__ == '__main__':
    
    #
    # close previous opened figures
    close('all')

    # Run the simulation
    to_record = [
        { 'pop': Excitatory, 'var': 'u' }, 
        { 'pop': Excitatory, 'var': 'v' },
        { 'pop': Excitatory, 'var': 'I' },
        { 'pop': Inhibitory, 'var': 'u' }, 
        { 'pop': Inhibitory, 'var': 'v' },
        { 'pop': Inhibitory, 'var': 'I' }        
    ]
    
    # 20-100ms is an input
    I = np.zeros((nb_steps,nb_exc_neurons))
    if nb_steps > 10:
        I[10:nb_steps,:] = 20.0 # 15mV as input
    
    record( to_record )
    for i in xrange(nb_steps):
        
        # first 20 ms no input
        Excitatory.I_in = I[i,:]    
        simulate(1)
        
    data = get_record( to_record )
    
    plot( Excitatory, data )
    plot( Inhibitory, data )
    
    show()