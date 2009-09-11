"""
My own variation on function-specific inspect-like features.
"""

# Author: Gael Varoquaux <gael dot varoquaux at normalesup dot org> 
# Copyright (c) 2009 Gael Varoquaux
# License: BSD Style, 3 clauses.

import itertools
import inspect


def get_func_code(func):
    """ Attempts to retrieve a reliable function code hash.
    
        The reason we don't use inspect.getsource is that it caches the
        source, whereas we want this to be modified on the fly when the
        function is modified.

        Returns
        -------
        func_code: string
            The function code
        source_file: string
            The path to the file in which the function is defined.
        first_line: int
            The first line of the code in the source file.

        Notes
        ------
        This function does a bit more magic than inspect, and is thus
        more robust.
    """
    source_file = None
    try:
        # Try to retrieve the source code.
        source_file = func.func_code.co_filename
        source_file_obj = file(source_file)
        first_line = func.func_code.co_firstlineno
        # All the lines after the function definition:
        source_lines = list(itertools.islice(source_file_obj, first_line-1, None))
        return ''.join(inspect.getblock(source_lines)), source_file, first_line
    except:
        # If the source code fails, we use the hash. This is fragile and
        # might change from one session to another.
        if hasattr(func, 'func_code'):
            return str(func.func_code.__hash__()), source_file, -1
        else:
            # Weird objects like numpy ufunc don't have func_code
            # This is fragile, as quite often the id of the object is
            # in the repr, so it might not persist accross sessions,
            # however it will work for ufuncs.
            return repr(func), source_file, -1


def get_func_name(func, resolv_alias=True):  
    """ Return the function import path (as a list of module names), and
        a name for the function.

        Parameters
        ----------
        func: callable
            The func to inspect
        resolv_alias: boolean, optional
            If true, possible local alias are indicated.
    """
    if hasattr(func, '__module__'):
        module = func.__module__
    else:
        try:
            module = inspect.getmodule(func)
        except TypeError:
            if hasattr(func, '__class__'):
                module = func.__class__.__module__
            else:
                module = 'unkown'
    if module is None:
        # Happens in doctests, eg
        module = ''
    module = module.split('.')
    if hasattr(func, 'func_name'):
        name = func.func_name
    elif hasattr(func, '__name__'): 
        name = func.__name__
    else:
        name = 'unkown'
    # Hack to detect functions not defined at the module-level
    if resolv_alias:
        # TODO: Maybe add a warning here?
        if hasattr(func, 'func_globals') and name in func.func_globals:
            if not func.func_globals[name] is func:
                name = '%s-alias' % name
    return module, name


# XXX: Needed to implement the 'ignore' functionality.
def filter_args(func, ignore_lst, *args, **kwargs):
    """ Filters the given args and kwargs using a list of arguments to
        ignore, and a function specification.

        Parameters
        ----------
        func: callable
            Function giving the argument specification
        ignore_lst: list of strings
            List of arguments to ignore (either a name of an argument 
            in the function spec, or '*', or '**')
        *args: list
            Positional arguments passed to the function.
        **kwargs: dict
            Keyword arguments passed to the function

        Returns
        -------
        filtered_args: list
            List of filtered positionnal arguments.
        filtered_kwdargs: dict
            List of filtered Keyword arguments.
    """
    args = list(args)
    arg_spec = inspect.getargspec(func)
    arg_names = arg_spec.args
    arg_defaults = arg_spec.defaults
    #arg_keywords = arg_spec.keywords or {}
    # XXX: Need to check that we have a valid argument list.
    arg_dict = dict()
    for arg_position, arg_name in enumerate(arg_names):
        if arg_position < len(args):
            arg_dict[arg_names] = args[arg_position]
        
    for item in ignore_lst:
        if item in arg_names:
            if item in kwargs:
                kwargs.pop(item)
            else:
                args.pop(arg_names.index(item))
        elif item == '*':
            " Must implement logic to get rid of *args "
        elif item == '**':
            " Must implement logic to get rid of **kwargs "
        else:
            module, name = get_func_name(func, resolv_alias=False)
            raise ValueError("Argument '%s' is not defined for f" % 
                            (item, 
                             inspect.formatargspec(arg_names,
                                                   arg_spec.varargs,
                                                   arg_spec.keywords,
                                                   arg_defaults,
                                                   )))
    return args, kwargs

