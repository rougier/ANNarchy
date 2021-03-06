#
#   ANNarchy - SpikeTest
#
#   a playroom for testing spike - related features.
#
#   authors: Helge Uelo Dinkelbach, Julien Vitay
#
from ANNarchy import *

from pylab import show, figure, subplot, legend, close

Izhikevitch = SpikeNeuron(
parameters="""
    noise_scale = 0.0 : population
    a = 0.02 : population
    b = 0.2 : population
    c = -65.0 : population
    d = 2.0 : population
    tau = 10.0 : population
""",
equations="""
    noise = Normal(0.0,1.0)
    I = g_exc + noise * noise_scale : init = 0.0
    tau * dg_exc / dt = -g_exc
    dv/dt = 0.04 * v * v + 5*v + 140 -u + I : init = -65.0
    du/dt = a * (b*v - u) : init = 0.2
""",
spike = """
    v >= 30.0
""",
reset = """
    v = c
    u = u+d
"""
)

Simple =SpikeSynapse(
pre_spike="""
    g_target += 1.0
"""              
)
 
SimpleLearn=SpikeSynapse(
parameters="""
    tau_pre = 5 : postsynaptic
    tau_post = 5 : postsynaptic
    cApre = 1 : postsynaptic
    cApost = -1 : postsynaptic
""",
equations = """
    tau_pre * dApre/dt = -Apre
    tau_post * dApost/dt = -Apost
""",
pre_spike="""
    Apre = Apre + cApre
    g_target += w
    w = w + Apost
""",                  
post_spike="""
    Apost = Apost + cApost
    w = w + Apre
"""      
)

Small = Population(3, Izhikevitch)
Small.noise_scale = 5.0
Middle = Population(1, Izhikevitch)
Middle.noise_scale = 5.0

testAll2AllSpike = Projection( 
    pre = Small, 
    post = Middle, 
    target = 'exc',
    synapse = SimpleLearn
).connect_all_to_all(weights=Uniform(0.0, 1.0), delays=50.0)

compile()

to_record = { Small : [ 'v', 'g_exc'],
              Middle :[ 'v', 'g_exc'] }

start_record ( to_record )

testAll2AllSpike.dendrite(0).start_record('Apre')
testAll2AllSpike.dendrite(0).start_record('Apost')
testAll2AllSpike.dendrite(0).start_record('w')

simulate(1000)

testAll2AllSpike.disable_learning()

simulate(1000)

testAll2AllSpike.enable_learning()

simulate(1000)

data = get_record( to_record )
Apre = testAll2AllSpike.dendrite(0).get_record('Apre')
Apost = testAll2AllSpike.dendrite(0).get_record('Apost')
weight = testAll2AllSpike.dendrite(0).get_record('w')


close('all')

#
#plot pre neurons
#===============================================================================
# for i in range(Small.size):
#     fig = figure()
#     fig.suptitle(Small.name+', neuron '+str(i))
#       
#     ax = subplot(211)
#       
#     ax.plot( data['Population0']['v']['data'][i,:], label = "membrane potential")
#     ax.legend(loc=2)
#       
#     ax = subplot(212)
#       
#     ax.plot( data['Population0']['g_exc']['data'][i,:], label = "g_exc")
#     ax.legend(loc=2)
#===============================================================================
 
#
# The synapse are not ordered ascending in relation to presynaptic ranks
# to correctly identify the data we need to take this in mind
pre_ranks = testAll2AllSpike.dendrite(0).rank
neur_col = ['b','g','r']

#
# plot post neurons
for i in range(Middle.size):
    fig = figure()
    fig.suptitle(Middle.name+', neuron '+str(i) + 'Apre, Apost')
     
    ax = subplot(811)
     
    ax.plot( data[ Middle ]['v']['data'][i,:], label = "membrane potential")
    ax.legend(loc=2)

    ax = subplot(812)
     
    ax.plot( data[ Middle ]['g_exc']['data'][i,:], label = "g_exc")
    ax.legend(loc=2)

    ax = subplot(813)
     
    ax.plot( data[ Small ]['v']['data'][0,:], label = "membrane potential (Pop0, n=0)", color=neur_col[pre_ranks[0]])
    ax.legend(loc=2)

    ax = subplot(814)
     
    ax.plot( data[ Small ]['v']['data'][1,:], label = "membrane potential (Pop0, n=1)", color=neur_col[pre_ranks[1]])
    ax.legend(loc=2)

    ax = subplot(815)
     
    ax.plot( data[ Small ]['v']['data'][2,:], label = "membrane potential (Pop0, n=2)", color=neur_col[pre_ranks[2]])
    ax.legend(loc=2)

    #
    # Apost    
    ax = subplot(816)
    ax.plot( Apost['data'][0,:], label = "Apost")
    ax.legend(loc=2)    

    #
    # Apre    
    ax = subplot(817)
    for j in range(Small.size):
        ax.plot( Apre['data'][j,:], label = "Apre ("+str(pre_ranks[j])+")", color=neur_col[j])
    ax.legend(loc=2)    

    #
    # w    
    ax = subplot(818)
    for j in range(Small.size):
        ax.plot( weight['data'][j,:], label = "w ("+str(pre_ranks[j])+")", color=neur_col[j])
    ax.legend(loc=2)    
 
for i in range(Middle.size):
    fig = figure()
    fig.suptitle(Middle.name+', neuron '+str(i)+' (conductance)')
      
    ax = subplot(511)
      
    ax.plot( data[ Middle ]['v']['data'][i,:], label = "membrane potential")
    ax.legend(loc=2)
 
    ax = subplot(512)
      
    ax.plot( data[ Middle ]['g_exc']['data'][i,:], label = "g_exc")
    ax.legend(loc=2)
 
    ax = subplot(513)
      
    ax.plot( data[ Small ]['v']['data'][0,:], label = "membrane potential (Pop0, n="+str(pre_ranks[0])+")", color='b')
    ax.legend(loc=2)
 
    ax = subplot(514)
      
    ax.plot( data[ Small ]['v']['data'][1,:], label = "membrane potential (Pop0, n="+str(pre_ranks[1])+")", color='g')
    ax.legend(loc=2)
 
    ax = subplot(515)
      
    ax.plot( data[ Small ]['v']['data'][2,:], label = "membrane potential (Pop0, n="+str(pre_ranks[2])+")", color='r')
    ax.legend(loc=2)
    
show()

print 'done'
raw_input()