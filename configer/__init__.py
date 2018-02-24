#!/usr/bin/python3
"""Simple package to help automate setting and checking variables.  """

__all__ = [ 'Configer' ]

class Configer:
    """A simple helper class for configuration variables.
    
    Configer stores four properties for every "configuration" the caller
    stores with in it:  name, default value, current value, and a validator
    function.  This is unlimited, so the caller can store as many
    "configurations" as needed in one Configer object.

    The constructor sets the name, default, and validator function.  If the
    validation fails, the constructor throws an exception.  Then, set() calls
    will validate the new value data using the validator function before
    setting the current value.  If the validation fails during set(), the
    current value is not changed.
    """

    def __init__(self, default):
        """Initialize configer.

        Parameters:
            default: a dict of dicts.  The key is the name of the configuration
                object to be used later.  The value is another dict containing
                the following keys: 'default', 'func'.  The value of key 'default'
                is the current and default value for this configuration.  The
                value of the key 'func' is a function that validates the value.

        Returns: An initialized Configer object.
        """
        for key in default.keys() :
            defaultVal = default[key]['default']
            if not default[key]['func'](defaultVal) :
                raise ValueError('New value failed validation: '+str(defaultVal))
            default[key]['currval'] = defaultVal    # copy default to currval

        self.c = default                            # adopt validated dict as config

    def set(self, name, value) :
        """Update a configuration stored in configer.

        Parameters:
        name : Name/ref/key of the configuration for which to change the value.
        value : The value to which the configuration will be set, after validation.
        """
        if key not in self.c.keys() :
            raise NameError('Invalid configuration name:'+str(name))
        validatorFunc = self.c[name]['func']
        if not validatorFunc(value) :
            raise NotImplementedError('Invalid configuration value:'+str(value))
        self.c[name]['currval'] = value

    def get(self, name) :
        """Return any value previously stored in configer.

        Parameters:
        name : Name of configuration to retrieve.

        Returns: Value corresponding to the name/ref/key specified.
        """
        if name not in self.c.keys() :
            raise NameError('Invalid configuration name:'+str(name))
        return self.c[name]['currval']

    def getConfig(self) :
        """Returns the current configuration, a dictionary """
        return self.c

    def isValid(self) :
        """Run all validation functions.  Returns False if any functions fail. """
        for key in self.c.keys() :
            validatorFunc = self.c[key]['func']             # get validator function
            if not validatorFunc(self.c[key]['currval']) :  # validate current value
                return False 
        return True
