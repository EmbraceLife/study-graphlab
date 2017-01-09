"""
This module provides Python-variable wrapping/exposing to GraphLab Canvas.
The find_vars decorator allows arbitrary functions to expose their local variables
to Canvas.
"""

from __future__ import absolute_import

import graphlab
import graphlab.canvas
import inspect
import six

def _find_variable_name(var):
    # climb up the stack two frames before checking for non-class variables
    frame = inspect.currentframe()
    try:
        frame = frame.f_back.f_back
        finalFrame = __climb_frame_stack(frame)
    except:
        finalFrame = frame

    variableDictionary = finalFrame.f_locals

    for k,v in six.iteritems(variableDictionary):
        if k.startswith('_'):
            # ignore underscore names, generated by IPython
            continue
        if graphlab.canvas._same_object(var, v):
            return (k,v)
            break
    return (None, None)

def find_vars(var):
    """
    Finds all the local variables in the caller, and for any that match
    GraphLab Create data structures, we will keep a reference (by name) in this module.
    Given a dictionary of local variables from a stack frame, identify which ones correspond to GraphLab
    Create data structures and store those in _vars so we can update the browser.
    """
    target = graphlab.canvas.get_target()
    (variable_name, variable) = _find_variable_name(var)
    if variable_name is not None:
        target.add_variable((variable_name,), variable)
    return variable_name


def __climb_frame_stack(frame):
    """

    """
    if ('self' in frame.f_locals.keys() or 'show' in frame.f_code.co_name):
        return __climb_frame_stack(frame.f_back)
    return frame