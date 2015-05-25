import logging
import inspect
import sys

active_breakpoints = []
func_breakpoints = {}

def activate_breakpoint(tags):
    """
    Active the breakpoints  for a given list of tags
    
    Parameters
    ----------
    tags: list
        List of tag names to activate
    
    Returns
    -------
    activate_break_points: list
        List of all active breakpoints
    """
    active_breakpoints.extend(tags)
    return active_breakpoints

class func_breakpoint:
    """
    Function wrapper for breakpoints. For example, executing ::
    
        import ipydebug
        @ipydebug.func_breakpoint('debug')
        def my_func(x,y,z):
            return x+y+z
    
    will activate a breakpoint for the function ``my_func`` so that each time it is called the
    ipython console will interrupt the code before the function is run. To access variables
    in the local scope where the breakpoint was set, use the ``local_vars`` variable,
    For example for the ``my_func`` function defined above ::
    
        >>>> my_func(1,2,z=3)
        
        In [1]: args
        Out[1]: (1,2)
        
        In [2]: kwargs
        Out[2]: {'z': 3}
        
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize a breakpoint function wrapper.
        
        Parameters
        ----------
        args: list
            Arguments used to initialize the `ipydebug.Breakpoint` associated with the function
        kwargs: dict
            Keyword arguments used to initialize the `ipydebug.Breakpoint` associated with 
            the function
        """
        self.args = args
        self.kwargs = kwargs
    def __call__(self, func):
        """
        When the function is called, call the breakpoint, then execute the function
        (unless ``self.breakpoint.exit=True``)
        """
        def inner(*args, **kwargs):
            """
            The wrapped function, called with any args and kwargs passed to the function.
            The args and kwargs are passed to the breakpoint function so that the
            user has access to them as variables.
            """
            self.breakpoint.break_here()
            return func(*args, **kwargs)
        # If this is the first time the function is called, add it to the breakpoint functions
        if inner.__name__ in func_breakpoints:
            self.breakpoint = func_breakpoints[inner.__name__]
        else:
            self.breakpoint = Breakpoint(*self.args, **self.kwargs)
        # Change the name of inner to be the name of the function that is being wrapped
        inner.__name__ = func.__name__
        return inner

class Breakpoint:
    """
    Defines a breakpoint in the code associated with a set of tags that can
    be turned on or off. A breakpoint will interrupt the code every time it is
    called if if it's ``activate`` property is ``True`` or  one of it's ``tags`` 
    in contained in `ipydebug.active_breakpoints`. 
    
    """
    def __init__(self, tags=[], activate_tags=True, activate=False, max_usage=10, exit=False,
            log=None):
        """
        Initialize the Breakpoint.
        
        Parameters
        ----------
        tags: list of strings
            List of tags associated with the breakpoint. If any of these tags is stored in
            active_breakpoints then the breakpoint will interrupt the code when it is
            encountered
        activate_tags: bool or list
            If ``activate_tags`` is a boolean True value then all of the ``tags`` associated
            with the class are added to ``active_breakpoints``. If ``activate_tags`` is a list
            then all of the tags in the list are added to ``active_breakpoints``.
        activate: bool
            Whether or not the breakpoint is always active. If ``activate==False`` then
            the breakpoint will only interrupt the code if one of it's tags is contained
            in ``active_breakpoints``.
        max_usage: int
            Maximum number of times a breakpoint will remain active. If ``max_usage==0`` then
            the breakpoint will always be active, otherwise after ``max_usage`` calls the 
            breakpoint will no longer interrupt the code. On the last use the user will be
            notified that the breakpoint is about to expire, at which point it could
            be reset by the user.
        exit: bool
            If ``exit==True`` the code will exit after the user exits the IPython console,
            otherwise the code will continue running.
        log: str or func
            If log is a string then logging.info will log the string when the breakpoint
            is called. If log is a function then when the breakpoint is called logging.info
            will log the result of the function, called with locals() as the argument 
            (allowing the user to log any of the local variables)
        """
        if activate_tags:
            if isinstance(activate_tags, bool):
                activate_breakpoint(tags)
            else:
                activate_breakpoint(activate_tags)
        # Number of times this breakpoint has been used
        self.breaks = 0
        self.tags = tags
        self.active = activate
        self.max_usage = max_usage
        self.exit = exit
        self.log = log
    
    def break_here(self, force=False, exit=False):
        """
        Interrupt the code at the present location.
        
        Parameters
        ----------
        force: bool
            If ``force==True`` the code will be interrupted even if the breakpoint is
            not activated and none of it's tags are in ``active_breakpoints``.
        exit: bool
            If ``exit==True`` the code will exit when the user exits the IPython
            console.
        """
        # Make the local variables from the function with the breakpoint
        # available in the local scope
        local_vars = inspect.stack()[1][0].f_locals
        for var in local_vars:
            locals()[var] = local_vars[var]
        # Log the breakpoint
        if self.log is not None:
            if inspect.isfunction(self.log):
                log = self.log(locals())
            else:
                log = self.log
            logging.debug(log)
        # Check to see if the breakpoint should interrupt the code
        if ((self.active or force or any([tag in active_breakpoints for tag in self.tags]))
                and (self.max_usage is None or self.breaks<self.max_usage)):
            self.breaks += 1
            if self.breaks==self.max_usage:
                logging.warning(("You have reached the maximum number of calls to "
                    "interrupt the code with this function. If you want to continue to "
                    "use this breakpoint you must modify self.breaks or self.max_usage\n\n"))
            try:
                import IPython
                IPython.embed()
            except ImportError:
                raise Exception("You must have ipython installed to use break points")
        if self.exit or exit:
            sys.exit()