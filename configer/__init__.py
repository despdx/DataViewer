#!/usr/bin/python3
"""Simple package to help automate setting and checking variables.  """

__all__ = [ 'Configer' ]

from functools import wraps
from warnings import warn
from sys import stderr
import logging
logging.basicConfig(level='WARNING')

class Configer(object):
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
        self.__config = dict()
        for key in default.keys() :
            ca = _ConfAtom(default[key])
            logging.debug('key:'+str(key))
            logging.debug('ca:'+str(ca))
            self.__config[key] = ca

    def get(self, name) :
        """Return value associated with the specified name/key/reference """
        return self.__config[name]

    def set(self, name, value) :
        """Update a configuration stored in configer.

        Parameters:
        name : Name/ref/key of the configuration for which to change the value.
        value : The value to which the configuration will be set, after validation.
        """
        self.__config[name] = value

    def getConfig(self) :
        """Returns the current configuration, a dictionary """
        return self.__config.copy()

    def isValid(self) :
        """Run all validation functions.  Returns False if any functions fail. """
        c = self.__config
        for key in c.keys() :
            if not c[key].isValid() :
                return False 
        return True

class _ConfAtom(object):
    """ Encapsulation class for individual settings """

    def __init__(self, initDict) :
        d = initDict['default']
        f = initDict['func']
        if f(d) :
            self.__default = d      # store default
            self.__validator = f    # store validator function
            self.__ca = d           # make default the current value
        else :
            raise ValueError("Default value failed validation: "+d)

    @property
    def ca(self) :
        return self.__ca

    @ca.setter
    def ca(self, newval) :
        if self.__validator(newval) :
            self.__ca = newval
        else :
            raise ValueError("Value failed validation: "+newval)

    def isValid(self) :
        if self.__validator(self.__ca) :
            return True
        else :
            return False

    def __repr__(self) :
        return repr(self.__ca)+'(Instance of _ConfAtom)'

    def __str__(self) :
        return str(self.__ca)
