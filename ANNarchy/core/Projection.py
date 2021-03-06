"""

    Projection.py

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
import numpy as np
import math
import copy, inspect

from ANNarchy.core import Global
from ANNarchy.core.Random import RandomDistribution
from ANNarchy.core.Dendrite import Dendrite
from ANNarchy.core.PopulationView import PopulationView
import ANNarchy.core.Connectors as ConnectorMethods


class Projection(object):
    """
    Represents all synapses of the same type between two populations.
    """

    def __init__(self, pre, post, target, synapse=None, name=None):
        """
        *Parameters*:

            * **pre**: pre-synaptic population (either its name or a ``Population`` object).
            * **post**: post-synaptic population (either its name or a ``Population`` object).
            * **target**: type of the connection.
            * **synapse**: a ``Synapse`` instance.
            * **name**: unique name of the projection (optional).

        By default, the synapse only ensures linear synaptic transmission:

        * For rate-coded populations: ``psp = w * pre.r``
        * For spiking populations: ``g_target += w``

        """

        # Store the pre and post synaptic populations
        # the user provide either a string or a population object
        # in case of string, we need to search for the corresponding object
        if isinstance(pre, str):
            for pop in Global._network[0]['populations']:
                if pop.name == pre:
                    self.pre = pop
        else:
            self.pre = pre

        if isinstance(post, str):
            for pop in Global._network[0]['populations']:
                if pop.name == post:
                    self.post = pop
        else:
            self.post = post

        # Store the arguments
        self.target = target

        # Add the target to the postsynaptic population
        self.post.targets.append(self.target)

        # check if a synapse description is attached
        if not synapse:
            # No synapse attached assume default synapse based on
            # presynaptic population.
            if self.pre.neuron_type.type == 'rate':
                from ANNarchy.models.Synapses import DefaultRateCodedSynapse
                self.synapse_type = DefaultRateCodedSynapse()
                self.synapse_type.type = 'rate'
            else:
                from ANNarchy.models.Synapses import DefaultSpikingSynapse
                self.synapse_type = DefaultSpikingSynapse()
                self.synapse_type.type = 'spike'

        elif inspect.isclass(synapse):
            self.synapse_type = synapse()
            self.synapse_type.type = self.pre.neuron_type.type
        else:
            self.synapse_type = copy.deepcopy(synapse)
            self.synapse_type.type = self.pre.neuron_type.type

        # Analyse the parameters and variables
        self.synapse_type._analyse()

        # Create a default name
        self.id = len(Global._network[0]['projections'])
        if name:
            self.name = name
        else:
            self.name = 'proj'+str(self.id)

        # Get a list of parameters and variables
        self.parameters = []
        self.init = {}
        for param in self.synapse_type.description['parameters']:
            self.parameters.append(param['name'])
            self.init[param['name']] = param['init']

        self.variables = []
        for var in self.synapse_type.description['variables']:
            self.variables.append(var['name'])
            self.init[var['name']] = var['init']

        self.attributes = self.parameters + self.variables

        # Add the population to the global network
        Global._network[0]['projections'].append(self)

        # Finalize initialization
        self.initialized = False

        # Cython instance
        self.cyInstance = None

        # Connectivity
        self._synapses = None
        self._connection_method = None
        self._connection_args = None
        self._connection_delay = None
        self._connector = None

        # If a single weight value is used
        self._single_constant_weight = False

        # If a dense matrix should be used instead of LIL
        self._dense_matrix = False

        # Recorded variables
        self.recorded_variables = {}

        # Reporting
        self.connector_name = "Specific"
        self.connector_description = "Specific"

        # Overwritten by derived classes, to add
        # additional code
        self._specific_template = {}

        # To allow case-specific adjustment of parallelization
        # parameters, e. g. openMP schedule, we introduce a
        # dictionary read by the ProjectionGenerator.
        #
        # Will be overwritten either by inherited classes or
        # by an omp_config provided to the compile() method.
        self._omp_config = {
            #'psp_schedule': 'schedule(dynamic)'
        }

    # Add defined connectors
    connect_one_to_one = ConnectorMethods.connect_one_to_one
    connect_all_to_all = ConnectorMethods.connect_all_to_all
    connect_gaussian = ConnectorMethods.connect_gaussian
    connect_dog = ConnectorMethods.connect_dog
    connect_fixed_probability = ConnectorMethods.connect_fixed_probability
    connect_fixed_number_pre = ConnectorMethods.connect_fixed_number_pre
    connect_fixed_number_post = ConnectorMethods.connect_fixed_number_post
    connect_with_func = ConnectorMethods.connect_with_func
    connect_from_matrix = ConnectorMethods.connect_from_matrix
    _load_from_matrix = ConnectorMethods._load_from_matrix
    connect_from_sparse = ConnectorMethods.connect_from_sparse
    _load_from_sparse = ConnectorMethods._load_from_sparse
    connect_from_file = ConnectorMethods.connect_from_file
    _load_from_csr = ConnectorMethods._load_from_csr

    def _generate(self):
        "Overriden by specific projections to generate the code"
        pass

    def _instantiate(self, module):
        "Instantiates the projection after compilation."
        self._connect(module)
        self.initialized = True

    def _init_attributes(self):
        """
        Method used after compilation to initialize the attributes. Called by Generator._instantiate
        """
        for name, val in self.init.items():
            if not name in ['w']:
                self.__setattr__(name, val)

    def _connect(self, module):
        """
        Builds up dendrites either from list or dictionary. Called by instantiate().
        """
        if not self._connection_method:
            Global._error('The projection between ' + self.pre.name + ' and ' + self.post.name + ' is declared but not connected.')
            exit(0)

        proj = getattr(module, 'proj'+str(self.id)+'_wrapper')
        self.cyInstance = proj(self._connection_method(*((self.pre, self.post,) + self._connection_args)))

        # Access the list of postsynaptic neurons
        self.post_ranks = self.cyInstance.post_rank()

    def _store_connectivity(self, method, args, delay):

        self._connection_method = method
        self._connection_args = args
        self._connection_delay = delay

        # Analyse the delay
        if isinstance(delay, (int, float)): # Uniform delay
            self.max_delay = int(delay/Global.config['dt'])
            self.uniform_delay = int(delay/Global.config['dt'])
        elif isinstance(delay, RandomDistribution): # Non-uniform delay
            self.uniform_delay = -1
            # Ensure no negative delays are generated
            if delay.min == None:
                delay.min = Global.config['dt']
            # The user needs to provide a max in order to compute max_delay
            if delay.max == None:
                Global._error('Projection.connect_xxx(): if you use a non-bounded random distribution for the delays (e.g. Normal), you need to set the max argument to limit the maximal delay.')
                exit(0)
            self.max_delay = int(delay.max/Global.config['dt'])
        elif isinstance(delay, (list, np.ndarray)): # connect_from_matrix/sparse
            self.uniform_delay = -1
            self.max_delay = int(max([max(l) for l in delay])/Global.config['dt'])
        else:
            Global._error('Projection.connect_xxx(): delays are not valid!')
            exit(0)

        # Transmit the max delay to the pre pop
        if isinstance(self.pre, PopulationView):
            self.pre.population.max_delay = max(self.max_delay, self.pre.population.max_delay)
        else:
            self.pre.max_delay = max(self.max_delay, self.pre.max_delay)


    def _has_single_weight(self):
        "If a single weight should be generated instead of a LIL"
        return self._single_constant_weight and not Global.config['structural_plasticity'] and not self.synapse_type.description['plasticity'] and Global.config['paradigm']=="openmp"


    def reset(self, synapses=False):
        """
        Resets all parameters and variables to the value they had before the call to compile.

        *Parameters*:

        * **synapses**: if True, the connections will also be erased (default: False).

        .. note::

            Not implemented yet...
        """
        self._init_attributes()
        if synapses:
            Global._warning('Resetting synapses is not implemented yet...')

    ################################
    ## Dendrite access
    ################################
    @property
    def size(self):
        "Number of post-synaptic neurons receiving synapses."
        if self.cyInstance:
            return len(self.post_ranks)
        else:
            return 0

    def __len__(self):
        " Number of postsynaptic neurons receiving synapses in this projection."
        return self.size

    @property
    def nb_synapses(self):
        "Total number of synapses in the projection."
        return sum([self.cyInstance.nb_synapses(n) for n in range(self.size)])


    @property
    def dendrites(self):
        """
        Iteratively returns the dendrites corresponding to this projection.
        """
        for idx, n in enumerate(self.post_ranks):
            yield Dendrite(self, n, idx)

    def dendrite(self, post):
        """
        Returns the dendrite of a postsynaptic neuron according to its rank.

        *Parameters*:

            * **post**: can be either the rank or the coordinates of the postsynaptic neuron
        """
        if not self.initialized:
            Global._error('dendrites can only be accessed after compilation.')
            exit(0)
        if isinstance(post, int):
            rank = post
        else:
            rank = self.post.rank_from_coordinates(post)

        if rank in self.post_ranks:
            return Dendrite(self, rank, self.post_ranks.index(rank))
        else:
            Global._error(" The neuron of rank "+ str(rank) + " has no dendrite in this projection.")
            return None

    def synapse(self, pre, post):
        """
        Returns the synapse between a pre- and a post-synaptic neuron if it exists, None otherwise.

        *Parameters*:

            * **pre**: rank of the pre-synaptic neuron.
            * **post**: rank of the post-synaptic neuron.
        """
        if not isinstance(pre, int) or not isinstance(post, int):
            Global._error('Projection.synapse() only accepts ranks for the pre and post neurons.')
        return self.dendrite(post).synapse(pre)


    # Iterators
    def __getitem__(self, *args, **kwds):
        """ Returns dendrite of the given position in the postsynaptic population.

        If only one argument is given, it is a rank. If it is a tuple, it is coordinates.
        """
        if len(args) == 1:
            return self.dendrite(args[0])
        return self.dendrite(args)

    def __iter__(self):
        " Returns iteratively each dendrite in the population in ascending postsynaptic rank order."
        for idx, n in enumerate(self.post_ranks):
            yield Dendrite(self, n, idx)

    ################################
    ## Access to attributes
    ################################

    @property
    def delay(self):
        if not hasattr(self.cyInstance, 'get_delay'):
            if self.max_delay <= 1 :
                return Global.config['dt']
            elif self.uniform_delay != -1:
                return self.uniform_delay * Global.config['dt']
        else:
            return [[pre * Global.config['dt'] for pre in post] for post in self.cyInstance.get_delay()]


    def get(self, name):
        """
        Returns a list of parameters/variables values for each dendrite in the projection.

        The list will have the same length as the number of actual dendrites (self.size), so it can be smaller than the size of the postsynaptic population. Use self.post_ranks to indice it.

        *Parameters*:

        * **name**: the name of the parameter or variable
        """
        return self.__getattr__(name)

    def set(self, value):
        """ Sets the parameters/variables values for each dendrite in the projection.

        For parameters, you can provide:

            * a single value, which will be the same for all dendrites.

            * a list or 1D numpy array of the same length as the number of actual dendrites (self.size).

        For variables, you can provide:

            * a single value, which will be the same for all synapses of all dendrites.

            * a list or 1D numpy array of the same length as the number of actual dendrites (self.size). The synapses of each postsynaptic neuron will take the same value.

        .. warning::

            It not possible to set different values to each synapse using this method. One should iterate over the dendrites::

                for dendrite in proj.dendrites:
                    dendrite.w = np.ones(dendrite.size)

        *Parameters*:

        * **value**: a dictionary with the name of the parameter/variable as key.

        """

        for name, val in value:
            self.__setattr__(name, val)

    def __getattr__(self, name):
        " Method called when accessing an attribute."
        if name == 'initialized' or not hasattr(self, 'initialized'): # Before the end of the constructor
            return object.__getattribute__(self, name)
        elif hasattr(self, 'attributes'):
            if name in ['plasticity', 'transmission', 'update']:
                return self._get_flag(name)
            if name in self.attributes:
                if not self.initialized:
                    return self.init[name]
                else:
                    return self._get_cython_attribute( name )
            else:
                return object.__getattribute__(self, name)
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        " Method called when setting an attribute."
        if name == 'initialized' or not hasattr(self, 'initialized'): # Before the end of the constructor
            object.__setattr__(self, name, value)
        elif hasattr(self, 'attributes'):
            if name in ['plasticity', 'transmission', 'update']:
                self._set_flag(name, bool(value))
                return
            if name in self.attributes:
                if not self.initialized:
                    self.init[name] = value
                else:
                    self._set_cython_attribute(name, value)
            else:
                object.__setattr__(self, name, value)
        else:
            object.__setattr__(self, name, value)

    def _get_cython_attribute(self, attribute):
        """
        Returns the value of the given attribute for all neurons in the population,
        as a list of lists having the same geometry as the population if it is local.

        Parameter:

        * *attribute*: should be a string representing the variables's name.

        """
        return getattr(self.cyInstance, 'get_'+attribute)()

    def _set_cython_attribute(self, attribute, value):
        """
        Sets the value of the given attribute for all post-synaptic neurons in the projection,
        as a NumPy array having the same geometry as the population if it is local.

        Parameter:

        * *attribute*: should be a string representing the variables's name.

        """
        if isinstance(value, np.ndarray):
            value = list(value)
        if isinstance(value, list):
            if len(value) == len(self.post_ranks):
                for idx, n in enumerate(self.post_ranks):
                    if not len(value[idx]) == self.cyInstance.nb_synapses(idx):
                        Global._error('The postynaptic neuron ' + str(n) + ' receives '+ str(self.cyInstance.nb_synapses(idx))+ ' synapses.')
                        exit(0)
                    getattr(self.cyInstance, 'set_dendrite_'+attribute)(idx, value[idx])
            else:
                Global._error('The projection has ' + self.size + ' post-synaptic neurons.')
        elif isinstance(value, RandomDistribution):
            for idx, n in enumerate(self.post_ranks):
                getattr(self.cyInstance, 'set_dendrite_'+attribute)(idx, value.get_values(self.cyInstance.nb_synapses(idx)))
        else: # a single value
            if attribute in self.synapse_type.description['local']:
                for idx, n in enumerate(self.post_ranks):
                    getattr(self.cyInstance, 'set_dendrite_'+attribute)(idx, value*np.ones(self.cyInstance.nb_synapses(idx)))
            else:
                getattr(self.cyInstance, 'set_'+attribute)(value*np.ones(len(self.post_ranks)))

    def _get_flag(self, attribute):
        "flags such as learning, transmission"
        return getattr(self.cyInstance, '_get_'+attribute)()

    def _set_flag(self, attribute, value):
        "flags such as learning, transmission"
        getattr(self.cyInstance, '_set_'+attribute)(value)

    ################################
    ## Variable flags
    ################################
    def set_variable_flags(self, name, value):
        """ Sets the flags of a variable for the projection.

        If the variable ``r`` is defined in the Synapse description through:

            w = pre.r * post.r : max=1.0

        one can change its maximum value with:

            proj.set_variable_flags('w', {'max': 2.0})

        For valued flags (init, min, max), ``value`` must be a dictionary containing the flag as key ('init', 'min', 'max') and its value.

        For positional flags (postsynaptic, implicit), the value in the dictionary must be set to the empty string '':

            proj.set_variable_flags('w', {'implicit': ''})

        A None value in the dictionary deletes the corresponding flag:

            proj.set_variable_flags('w', {'max': None})


        *Parameters*:

        * **name**: the name of the variable.

        * **value**: a dictionary containing the flags.

        """
        rk_var = self._find_variable_index(name)
        if rk_var == -1:
            Global._error('The projection '+self.name+' has no variable called ' + name)
            return

        for key, val in value.items():
            if val == '': # a flag
                try:
                    self.synapse_type.description['variables'][rk_var]['flags'].index(key)
                except: # the flag does not exist yet, we can add it
                    self.synapse_type.description['variables'][rk_var]['flags'].append(key)
            elif val == None: # delete the flag
                try:
                    self.synapse_type.description['variables'][rk_var]['flags'].remove(key)
                except: # the flag did not exist, check if it is a bound
                    if has_key(self.synapse_type.description['variables'][rk_var]['bounds'], key):
                        self.synapse_type.description['variables'][rk_var]['bounds'].pop(key)
            else: # new value for init, min, max...
                if key == 'init':
                    self.synapse_type.description['variables'][rk_var]['init'] = val
                    self.init[name] = val
                else:
                    self.synapse_type.description['variables'][rk_var]['bounds'][key] = val



    def set_variable_equation(self, name, equation):
        """ Changes the equation of a variable for the projection.

        If the variable ``w`` is defined in the Synapse description through:

            eta * dw/dt = pre.r * post.r

        one can change the equation with:

            proj.set_variable_equation('w', 'eta * dw/dt = pre.r * (post.r - 0.1) ')

        Only the equation should be provided, the flags have to be changed with ``set_variable_flags()``.

        .. warning::

            This method should be used with great care, it is advised to define another Synapse object instead.

        *Parameters*:

        * **name**: the name of the variable.

        * **equation**: the new equation as string.
        """
        rk_var = self._find_variable_index(name)
        if rk_var == -1:
            Global._error('The projection '+self.name+' has no variable called ' + name)
            return
        self.synapse_type.description['variables'][rk_var]['eq'] = equation


    def _find_variable_index(self, name):
        " Returns the index of the variable name in self.synapse_type.description['variables']"
        for idx in range(len(self.synapse_type.description['variables'])):
            if self.synapse_type.description['variables'][idx]['name'] == name:
                return idx
        return -1

    ################################
    ## Learning flags
    ################################
    def enable_learning(self, period=None, offset=None):
        """
        Enables learning for all the synapses of this projection.

        *Parameters*:

        * **period** determines how often the synaptic variables will be updated.
        * **offset** determines the offset at which the synaptic variables will be updated relative to the current time.

        For example, providing the following parameters at time 10 ms::

            enable_learning(period=10., offset=5.)

        would call the updating methods at times 15, 25, 35, etc...

        The default behaviour is that the synaptic variables are updated at each time step. The parameters must be multiple of ``dt``
        """
        # Check arguments
        if period != None and offset!=None:
            if offset >= period:
                Global._error('enable_learning(): the offset must be smaller than the period.')
                exit(0)
        if period == None and offset!=None:
            Global._error('enable_learning(): if you define an offset, you have to define a period.')
            exit(0)
        try:
            self.cyInstance._set_update(True)
            self.cyInstance._set_plasticity(True)
            if period != None:
                self.cyInstance._set_update_period(int(period/Global.config['dt']))
            else:
                self.cyInstance._set_update_period(int(1))
                period = Global.config['dt']
            if offset != None:
                relative_offset = Global.get_time() % period + offset
                self.cyInstance._set_update_offset(int(relative_offset%period))
            else:
                self.cyInstance._set_update_offset(int(0))
        except:
            Global._warning('Enable_learning() is only possible after compile()')

    def disable_learning(self, update=None):
        """
        Disables learning for all synapses of this projection.

        The effect depends on the rate-coded or spiking nature of the projection:

        * **Rate-coded**: the updating of all synaptic variables is disabled (including the weights ``w``). This is equivalent to ``proj.update = False``.

        * **Spiking**: the updating of the weights ``w`` is disabled, but all other variables are updated. This is equivalent to ``proj.plasticity = False``.

        This method is useful when performing some tests on a trained network without messing with the learned weights.
        """
        try:
            if self.synapse_type.type == 'rate':
                self.cyInstance._set_update(False)
            else:
                self.cyInstance._set_plasticity(False)
        except Exception as e:
            Global._warning('disabling learning is only possible after compile().')


    ################################
    ## Methods on connectivity matrix
    ################################

    def save_connectivity(self, filename):
        """
        Saves the projection pattern in a file.

        Only the connectivity matrix, the weights and delays are saved, not the other synaptic variables.

        The generated data should be used to create a projection in another network::

            proj.connect_from_file(filename)

        *Parameters*:

        * **filename**: file where the data will be saved.
        """
        if not self.initialized:
            Global._error('save_connectivity(): the network has not been compiled yet.')
            return
        
        data = {
                'name': self.name,
                'post_ranks': self.post_ranks,
                'pre_ranks': self.cyInstance.pre_rank_all(), # was: [self.cyInstance.pre_rank(n) for n in range(self.size)],
                'w': self.cyInstance.get_w(),
                'delay': self.cyInstance.get_delay() if hasattr(self.cyInstance, 'get_delay') else None,
                'max_delay': self.max_delay,
                'uniform_delay': self.uniform_delay,
                'size': self.size,
                'nb_synapses': sum([self.cyInstance.nb_synapses(n) for n in range(self.size)])
            }
        try:
            import cPickle as pickle # Python2
        except:
            import pickle # Python3
        with open(filename, 'wb') as wfile:
            pickle.dump(data, wfile, protocol=pickle.HIGHEST_PROTOCOL)

    def _save_connectivity_as_csv(self):
        """
        Saves the projection pattern in the csv format.

        Please note, that only the pure connectivity data pre_rank, post_rank, w and delay are stored.
        """
        filename = self.pre.name + '_' + self.post.name + '_' + self.target+'.csv'

        with open(filename, mode='w') as w_file:

            for dendrite in self.dendrites:
                rank_iter = iter(dendrite.rank)
                w_iter = iter(dendrite.w)
                delay_iter = iter(dendrite.delay)
                post_rank = dendrite.post_rank

                for i in xrange(dendrite.size):
                    w_file.write(str(next(rank_iter))+', '+
                                 str(post_rank)+', '+
                                 str(next(w_iter))+', '+
                                 str(next(delay_iter))+'\n'
                                 )

    def _comp_dist(self, pre, post):
        """
        Compute euclidean distance between two coordinates.
        """
        res = 0.0

        for i in range(len(pre)):
            res = res + (pre[i]-post[i])*(pre[i]-post[i]);

        return res


    def receptive_fields(self, variable = 'w', in_post_geometry = True):
        """
        Gathers all receptive fields within this projection.

        *Parameters*:

        * **variable**: name of variable
        * **in_post_geometry**: if set to false, the data will be plotted as square grid. (default = True)
        """
        if in_post_geometry:
            x_size = self.post.geometry[1]
            y_size = self.post.geometry[0]
        else:
            x_size = int( math.floor(math.sqrt(self.post.size)) )
            y_size = int( math.ceil(math.sqrt(self.post.size)) )


        def get_rf(rank): # TODO: IMPROVE
            res = np.zeros( self.pre.size )
            for n in xrange(len(self.post_ranks)):
                if self.post_ranks[n] == n:
                    pre_ranks = self.cyInstance.pre_rank(n)
                    data = getattr(self.cyInstance, 'get_dendrite_'+variable)(rank)
                    for j in xrange(len(pre_ranks)):
                        res[pre_ranks[j]] = data[j]
            return res.reshape(self.pre.geometry)

        res = np.zeros((1, x_size*self.pre.geometry[1]))
        for y in xrange ( y_size ):
            row = np.concatenate(  [ get_rf(self.post.rank_from_coordinates( (y, x) ) ) for x in range ( x_size ) ], axis = 1)
            res = np.concatenate((res, row))

        return res

    def connectivity_matrix(self, fill=0.0):
        """
        Returns a dense connectivity matrix (2D Numpy array) representing the connections between the pre- and post-populations.

        The first index of the matrix represents post-synaptic neurons, the second the pre-synaptic ones.

        If PopulationViews were used for creating the projection, the matrix is expanded to the whole populations by default.

        *Parameters*:

        * **fill**: value to put in the matrix when there is no connection (default: 0.0).
        """
        if isinstance(self.pre, PopulationView):
            size_pre = self.pre.population.size
        else:
            size_pre = self.pre.size
        if isinstance(self.post, PopulationView):
            size_post = self.post.population.size
        else:
            size_post = self.post.size

        res = np.ones((size_post, size_pre)) * fill
        for rank in self.post_ranks:
            idx = self.post_ranks.index(rank)
            try:
                preranks = self.cyInstance.pre_rank(idx)
                w = self.cyInstance.get_dendrite_w(idx)
            except:
                Global._error('The connectivity matrix can only be accessed after compilation')
                return []
            res[rank, preranks] = w
        return res


    ################################
    ## Save/load methods
    ################################

    def _data(self):
        "Method gathering all info about the projection when calling save()"

        if not self.initialized:
            Global._error('save_connectivity(): the network has not been compiled yet.')
            return {}

        desc = {}
        desc['name'] = self.name
        desc['post_ranks'] = self.post_ranks
        desc['attributes'] = self.attributes
        desc['parameters'] = self.parameters
        desc['variables'] = self.variables
        desc['pre_ranks'] = self.cyInstance.pre_rank_all()

        # Attributes to save
        attributes = self.attributes
        if not 'w' in self.attributes:
            attributes.append('w')

        # Save all attributes
        for var in attributes:
            try:
                desc[var] = getattr(self.cyInstance, 'get_'+var)()
            except Exception as e:
                Global._error('Can not save the attribute ' + var + ' in the projection.')

        return desc


        # synapse_count = []
        # dendrites = []

        # for d in self.post_ranks:
        #     dendrite_desc = {}
        #     # Number of synapses in the dendrite
        #     synapse_count.append(self.dendrite(d).size)
        #     # Postsynaptic rank
        #     dendrite_desc['post_rank'] = d
        #     # Number of synapses
        #     dendrite_desc['size'] = self.cyInstance.nb_synapses(d)
        #     # Attributes
        #     attributes = self.attributes
        #     if not 'w' in self.attributes:
        #         attributes.append('w')
        #     # Save all attributes
        #     for var in attributes:
        #         try:
        #             dendrite_desc[var] = getattr(self.cyInstance, 'get_dendrite_'+var)(d)
        #         except Exception as e:
        #             Global._error('Can not save the attribute ' + var + ' in the projection.')
        #     # Add pre-synaptic ranks and delays
        #     dendrite_desc['rank'] = self.cyInstance.pre_rank(d)
        #     if hasattr(self.cyInstance, 'get_delay'):
        #         dendrite_desc['delay'] = self.cyInstance.get_delay()
        #     # Finish
        #     dendrites.append(dendrite_desc)

        # desc['dendrites'] = dendrites
        # desc['number_of_synapses'] = synapse_count

        # return desc

    def save(self, filename):
        """
        Saves all information about the projection (connectivity, current value of parameters and variables) into a file.

        * If the extension is '.mat', the data will be saved as a Matlab 7.2 file. Scipy must be installed.

        * If the extension ends with '.gz', the data will be pickled into a binary file and compressed using gzip.

        * Otherwise, the data will be pickled into a simple binary text file using pickle.

        *Parameter*:

        * **filename**: filename, may contain relative or absolute path.

            .. warning::

                The '.mat' data will not be loadable by ANNarchy, it is only for external analysis purpose.

        Example::

            proj.save('pop1.txt')

        """
        from ANNarchy.core.IO import _save_data
        _save_data(filename, self._data())


    def load(self, filename):
        """
        Loads the saved state of the projection.

        Warning: Matlab data can not be loaded.

        *Parameters*:

        * **filename**: the filename with relative or absolute path.

        Example::

            proj.load('pop1.txt')

        """
        from ANNarchy.core.IO import _load_data, _load_proj_data
        _load_proj_data(self, _load_data(filename))


    ################################
    ## Structural plasticity
    ################################
    def start_pruning(self, period=None):
        """
        Starts pruning the synapses in the projection if the synapse defines a 'pruning' argument.

        'structural_plasticity' must be set to True in setup().

        *Parameters*:

        * **period**: how often pruning should be evaluated (default: dt, i.e. each step)
        """
        if not period:
            period = Global.config['dt']
        if not self.cyInstance:
            Global._error('Can not start pruning if the network is not compiled.')
            exit(0)
        if Global.config['structural_plasticity']:
            try:
                self.cyInstance.start_pruning(int(period/Global.config['dt']), Global.get_current_step())
            except :
                Global._error("The synapse does not define a 'pruning' argument.")
                exit(0)
        else:
            Global._error("You must set 'structural_plasticity' to True in setup() to start pruning connections.")
            exit(0)

    def stop_pruning(self):
        """
        Stops pruning the synapses in the projection if the synapse defines a 'pruning' argument.

        'structural_plasticity' must be set to True in setup().
        """
        if not self.cyInstance:
            Global._error('Can not stop pruning if the network is not compiled.')
            exit(0)
        if Global.config['structural_plasticity']:
            try:
                self.cyInstance.stop_pruning()
            except:
                Global._error("The synapse does not define a 'pruning' argument.")
                exit(0)
        else:
            Global._error("You must set 'structural_plasticity' to True in setup() to start pruning connections.")
            exit(0)

    def start_creating(self, period=None):
        """
        Starts creating the synapses in the projection if the synapse defines a 'creating' argument.

        'structural_plasticity' must be set to True in setup().

        *Parameters*:

        * **period**: how often creating should be evaluated (default: dt, i.e. each step)
        """
        if not period:
            period = Global.config['dt']
        if not self.cyInstance:
            Global._error('Can not start creating if the network is not compiled.')
            exit(0)
        if Global.config['structural_plasticity']:
            try:
                self.cyInstance.start_creating(int(period/Global.config['dt']), Global.get_current_step())
            except:
                Global._error("The synapse does not define a 'creating' argument.")
                exit(0)
        else:
            Global._error("You must set 'structural_plasticity' to True in setup() to start creating connections.")
            exit(0)

    def stop_creating(self):
        """
        Stops creating the synapses in the projection if the synapse defines a 'creating' argument.

        'structural_plasticity' must be set to True in setup().
        """
        if not self.cyInstance:
            Global._error('Can not stop creating if the network is not compiled.')
            exit(0)
        if Global.config['structural_plasticity']:
            try:
                self.cyInstance.stop_creating()
            except:
                Global._error("The synapse does not define a 'creating' argument.")
                exit(0)
        else:
            Global._error("You must set 'structural_plasticity' to True in setup() to start creating connections.")
            exit(0)
