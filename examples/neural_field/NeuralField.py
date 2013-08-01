#
#
#    ANNarchy-4 NeuralField
#
#
from ANNarchy4 import *

#
# Define the neuron classes
#
Input = Neuron(   
    tau = 1.0,
    noise = 0.5,
    baseline = Variable(init = 0.0),
    mp = Variable(eq = "tau * dmp / dt + mp = baseline + noise * (2 * RandomDistribution('uniform', [0,1]) -1)"),
    rate = Variable(eq = "rate = pos(mp)"),
    order = ['mp','rate'] 
)

Focus = Neuron( 
    tau = 20.0,
    noise = 0.0,
    baseline = 0.0,
    threshold_min = 0.0,
    threshold_max = 1.0,
    mp = Variable(eq = "tau * dmp / dt + mp = sum(exc) - sum(inh) + baseline + noise * (2 * RandomDistribution('uniform', [0,1]) - 1) "),
    rate = Variable(eq = "rate = if mp > threshold_max then threshold_max else pos(mp)", init = 0.0),
    order = ['mp', 'rate']
)

ReversedSynapse = Synapse( 
    alpha = Variable(eq="dalpha/dt = post.rate - alpha", init=1.0),
    value = Variable(eq="dvalue/dt = pre.rate * post.rate - alpha"),
    psp = Variable(eq ="psp=(1 - pre.rate) * value") 
)
				
InputPop = Population("Input", (20,20,1), Input)
FocusPop = Population("Focus", (20,20,1), Focus)

Proj1 = Projection( pre = InputPop, post = "Focus", target = 'exc', 
                    connector = Connector( type='One2One', weights=RandomDistribution('constant', [1.0]) ) ,    
                    synapse=ReversedSynapse)
                    
Proj2 = Projection( pre = "Focus", post = "Focus", target = 'inh', 
                    connector = Connector( type='DoG', weights=RandomDistribution('uniform', [0,1]), 
                                           amp_pos=0.2, sigma_pos=0.1, amp_neg=0.1, sigma_neg=0.7 ) )

# Main program
if __name__ == "__main__":

    # Analyse and compile everything, initialize the parameters/variables...
    compile()
    
    import pyximport; pyximport.install()
    import BubbleWorld
    
    BubbleWorld.run(InputPop, FocusPop)
