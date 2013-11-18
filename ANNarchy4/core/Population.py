"""

    Population.py
    
    This file is part of ANNarchy.
    
    Copyright (C) 2013-2016  Julien Vitay <julien.vitay@gmail.com>,
    Helge Uelo Dinkelbach <helge.dinkelbach@gmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    ANNarchy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
"""
import Global 
import Neuron
from ANNarchy4 import generator
from ANNarchy4.core.Descriptor import Descriptor, Attribute
from ANNarchy4.core.PopulationView import PopulationView
from ANNarchy4.core.Random import RandomDistribution

import traceback
import numpy as np

class Population(Descriptor):
    """
    Represents a population of neurons.
    """

    def __init__(self, geometry, neuron, name=None):
        """
        Constructor of the population.
        
        *Parameters*:
        
            * *geometry*: population geometry as tuple. If an integer is given, it is the size of the population.

            * *neuron*: instance of ``ANNarchy4.Neuron``

            * *name*: unique name of the population (optional).
        
        """
        if isinstance(geometry, int): # 1D
            self.geometry = (geometry, )
        else: # a tuple is given
            self.geometry = geometry
            
        self.neuron_type = neuron
        self.id = len(Global._populations)
        if name:
            self.name = name
        else:
            self.name = 'Population'+str(self.id)
        
        if neuron.spike_vars == 0:
            self.generator = generator.MeanPopulation(self)            
        elif neuron.spike_vars == 1:
            self.generator = generator.SpikePopulation(self)                        
        else:
            print 'Error: only one SpikeVariable is allowed per neuron'
            exit(0)
            
        Global._populations.append(self)
        self._recorded_variables = []
        self.initialized = True        
        
    def _init_attributes(self):
        """ Method used after compilation to initialize the attributes."""
        for var in self.variables + self.parameters:
            setattr(self, var, Attribute(var))

    @property
    def width(self):
        if self.dimension >= 1:
            return self.geometry[0]
        else:
            print 'WARNING: insufficient dimension'
            return 1

    @property
    def height(self):
        if self.dimension >= 2:
            return self.geometry[1]
        else:
            print 'WARNING: insufficient dimension' 
            return 1

    @property
    def depth(self):
        if self.dimension == 3:
            return self.geometry[2]
        else:
            print 'WARNING: insufficient dimension' 
            return 1
        
    @property
    def cpp_class(self):
        return self.generator.class_name
    
    @property
    def variables(self):
        """
        Returns a list of all variable names.
        """
        ret_var=[] #default        
        
        #check additional variables
        neur_var = self.generator.neuron_variables
        for var in neur_var:
            if 'var' in var.keys():
                ret_var.append(var['name'])      
                
        return ret_var

    @property
    def parameters(self):
        """
        Returns a list of all parameter names.
        """
        neur_var = self.generator.neuron_variables
        ret_par=[]        
        for var in neur_var:
            if not 'var' in var.keys():
                ret_par.append(var['name'])
        return ret_par
        
    @property
    def size(self):
        """
        Number of neurons in the population.
        """
        size = 1
        for i in xrange(len(self.geometry)):
            size *= self.geometry[i]
        return size
        
    def __len__(self):
        """
        Number of neurons in the population.
        """
        return self.size

    @property
    def dimension(self):
        """
        Dimension of the population (1, 2 or 3)
        """
        return len(self.geometry)
        
    def reset(self):
        """
        Reset the population variables to their initial values.
        """
        try:
            self.cyInstance.reset()
        except:
            print 'reset population', self.name, 'failed.'
        
    def start_record(self, variable):
        """
        Start recording the previous defined variables.
        
        Parameter:
            
            * *variable*: single variable name or list of variable names.        
        """
        _variable = []
        
        if isinstance(variable, str):
            _variable.append(variable)
        elif isinstance(variable, list):
            _variable = variable
        else:
            print 'Error: variable must be either a string or list of strings.'
        
        for var in _variable:
            
            if not var in self.variables + self.parameters:
                print var,'is not an attribute of',self.name
                continue
            
            try:
                import ANNarchyCython
                print 'start record of', var
                exec('self.cyInstance._start_record_'+var+'()')
            except:
                print "Error: only possible after compilation."

    def stop_record(self, variable):
        """
        Stops recording the previous defined variables.

        Parameter:
            
            * *variable*: single variable name or list of variable names.        

        """
        _variable = []
        if isinstance(variable, str):
            _variable.append(variable)
        elif isinstance(variable, list):
            _variable = variable
        else:
            print 'Error: variable must be either a string or list of strings.'       
        
        for var in _variable:
            
            if not var in self.variables + self.parameters:
                print var,'is not an attribute of',self.name
                continue
            
            try:
                import ANNarchyCython
                exec('self.cyInstance._stop_record_'+var+'()')
            except:
                print 'stop record of', var
                print "Error: only possible after compilation."

    def get_record(self, variable):
        """
        Returns the recorded data as list of matrices. 

        Parameter:
            
            * *variable*: single variable name or list of variable names.        
        
        """
        _variable = []
        if isinstance(variable, str):
            _variable.append(variable)
        elif isinstance(variable, list):
            _variable = variable
        else:
            print 'Error: variable must be either a string or list of strings.'
        
        data_dict = {}
        
        for var in _variable:

            if not var in self.variables + self.parameters:
                print var,'is not an attribute of',self.name
                continue
            
            try:
                import ANNarchyCython
                data = eval('self.cyInstance._get_recorded_'+var+'()')
                
                tmp = []
                for i in xrange(data.shape[0]):
                    tmp.append(data[i,:].reshape(self.geometry))
                 
                data_dict[var] = tmp
                
            except:
                print 'get record of', var
                print "Error: only possible after compilation."

        return data_dict
        
    def get_variable(self, variable):
        """
        Returns the value of the given variable for all neurons in the population, as a NumPy array having the same geometry as the population.
        
        Parameter:
        
            * *variable*: should be a string representing the variables's name.
        """
        if hasattr(self, 'cyInstance'):
            if hasattr(self.cyInstance, variable):
                return getattr(self.cyInstance, variable).reshape(self.geometry)
            else:
                print 'Error: variable',variable,'does not exist in this population.'
                print traceback.print_stack()
        else:
            print 'Error: the network is not compiled yet.'
            print traceback.print_stack()
            
    def get_parameter(self, parameter):
        """
        Returns the value of the given variable for all neurons in the population, as a NumPy array having the same geometry as the population.
        
        Parameter:
        
            * *parameter*: should be a string representing the variables's name.
        """
        
        if hasattr(self, 'cyInstance'):
            if hasattr(self.cyInstance, parameter):
                return getattr(self.cyInstance, parameter)
            else:
                print 'Error: parameter',parameter,'does not exist in this population.'
                print traceback.print_stack()
        else:
            print 'Error: the network is not compiled yet.'
            print traceback.print_stack()
    
    def rank_from_coordinates(self, coord):
        """
        Returns rank corresponding to the given coordinates.
        
        Parameter:
        
            * *coord*: coordinate tuple, can be multidimensional.
        """
        # Check the coordinates
        if not len(coord) == self.dimension:
            print 'Error when accessing neuron', str(coord), ': the population', self.name , 'has only', self.size, 'neurons (geometry '+ str(self.geometry) +').'
            return None
        for d in range(len(coord)):
            if not coord[d] < self.geometry[d]:
                print 'Error when accessing neuron', str(coord), ': the population' , self.name , 'has only', self.size, 'neurons (geometry '+ str(self.geometry) +').'
                return None
        # Return the rank
        return np.ravel_multi_index( coord, self.geometry)

    def coordinates_from_rank(self, rank):
        """
        Returns a tuple representing the spatial coordinates corresponding to the geometry of the population.
        """
        # Check the rank
        if not rank < self.size:
            print 'Error: the given rank', str(rank), 'is larger than the size of the population', str(self.size) + '.'
            return None
        coord = np.unravel_index(rank, self.geometry)
        return coord

    def normalized_coordinates_from_rank(self, pos, norm=1.):
        """
        Returns a tuple of coordinates corresponding to the rank or coordinates, normalized between 0.0 and norm in each dimension.
        """
        if isinstance(pos, int):
            coord = self.coordinates_from_rank(pos)
        else:
            coord = pos
            
        normal = tuple()
        for dim in range(self.dimension):
            if self.geometry[dim] > 1:
                normal += ( norm * float(coord[dim])/float(self.geometry[dim]-1), )
            else:
                normal += (0.0,) # default?

        #print self.geometry,'=> (1.0,1.0):',coord,'=>', normal               
        return normal

    def set(self, value):
        """
        Sets neuron variable/parameter values.
        
        Parameter:
        
            * *value*: dictionary of attributes to be updated
            
                .. code-block:: python
                
                    set( 'tau' : 20, 'rate'= np.random.rand((8,8)) } )
        """
        if hasattr(self, 'cyInstance'):
            for val_key in value.keys():
                if hasattr(self, val_key):
                    # Check the type of the data
                    if isinstance(value[val_key], RandomDistribution):
                        val = value[val_key].getValues(self.size) 
                    else: 
                        val = value[val_key] 
                    setattr(self.cyInstance, val_key, val)
                else:
                    print "Error: population does not have the attribute: " + val_key + "."
        else:
            print 'Error: the network is not compiled yet.'
            print traceback.print_stack()
        
    def get(self, value):
        """
        Gets current variable/parameter values.
        
        Parameter:
        
            * *value*: value name as string
        """
        if hasattr(self, 'cyInstance'):
            if value in self.variables:
                return self.get_variable(value)
            elif value in self.parameters:
                return self.get_parameter(value)
            else:
                print "Error: population does not contain attribute: '"+value+"'"   
        else:
            print 'Error: the network is not compiled yet.'
            print traceback.print_stack()
            
#    def _reshape_vector(self, vector):
#        """
#        Transfers a list or a 1D np.array (indiced with ranks) into the correct 1D, 2D, 3D np.array
#        """
#        return np.array(vector).reshape(self.geometry)
            
    def neuron(self, coord):  
        " Returns neuron of coordinates coord in the population. If only one argument is given, it is the rank."  
    
        # Transform arguments
        if isinstance(coord, int):
            rank = coord
            if not rank < self.size:
                print 'Error when accessing neuron', str(rank), ': the population', self.name, 'has only', self.size, 'neurons (geometry '+ str(self.geometry) +').'
                return None
        else: # a tuple
            rank = self.rank_from_coordinates( coord )
            if rank == None:
                return None
        # Return corresponding neuron
        return Neuron.IndividualNeuron(self, rank)
        
          
    def neurons(self):
        """ Returns iteratively each neuron in the population.
        
        For instance, if you want to iterate over all neurons of a population:
        
            >>> for neur in pop.neurons():
            ...     print neur.rate
            
        Alternatively, one could also benefit from the ``__iter__`` special command. The following code is equivalent:
        
            >>> for neur in pop:
            ...     print neur.rate               
        """
        for n in range(self.size):
            yield self.neuron(n)
            
    # Iterators
    def __getitem__(self, *args, **kwds):
        """ Returns neuron of coordinates (width, height, depth) in the population. 
        
        If only one argument is given, it is a rank. 
        
        If slices are given, it returns a PopulationView object.
        """
        indices =  args[0]
        if isinstance(indices, int): # a single neuron
            return self.neuron(indices)
        elif isinstance(indices, slice): # a slice of ranks
            start, stop, step = indices.start, indices.stop, indices.step
            if indices.start is None:
                start=0
            if indices.stop is None:
                stop=self.size
            if indices.step is None:
                step=1
            rk_range = list(range(start, stop, step))
            return PopulationView(self, rk_range)
        elif isinstance(indices, tuple): # a tuple
            slices = False
            for idx in indices: # check if there are slices in the coordinates
                if isinstance(idx, slice): # there is at least one
                    slices = True
            if not slices: # return one neuron
                return self.neuron(indices)
            else: # Compute a list of ranks from the slices 
                coords=[]
                # Expand the slices
                for rk in range(len(indices)):
                    idx = indices[rk]
                    if isinstance(idx, int): # no slice
                        coords.append([idx])
                    elif isinstance(idx, slice): # slice
                        start, stop, step = idx.start, idx.stop, idx.step
                        if idx.start is None:
                            start=0
                        if idx.stop is None:
                            stop=self.geometry[rk]
                        if idx.step is None:
                            step=1
                        rk_range = list(range(start, stop, step))
                        coords.append(rk_range)
                # Generate all ranks from the indices
                if self.dimension ==2:
                    ranks = [self.rank_from_coordinates((x, y)) for x in coords[0] for y in coords[1]]
                elif self.dimension == 3:
                    ranks = [self.rank_from_coordinates((x, y, z)) for x in coords[0] for y in coords[1] for y in coords[2]]
                if not max(ranks) < self.size:
                    print 'Error: indices do not match the geometry of the population', str(self.geometry)
                    return 
                return PopulationView(self, ranks)
                
    def __iter__(self):
        " Returns iteratively each neuron in the population in ascending rank order."
        for n in range(self.size):
            yield self.neuron(n)  


