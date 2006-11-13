import copy
import sys

import scipy

import SloppyCell.KeyedList_mod as KeyedList_mod
import SloppyCell.Utility as Utility
KeyedList = KeyedList_mod.KeyedList

def fmin_powell_log_params(m, params, *args, **kwargs):
    func = m.cost_log_params

    pmin = scipy.optimize.fmin_powell(func, scipy.log(params), 
                                      *args, **kwargs)
    if isinstance(params, KeyedList):
        pout = params.copy()
        pout.update(scipy.exp(pmin))
        return pout
    else:
        return scipy.exp(pmin)

def fmin_log_params(m, params, *args, **kwargs):
    def func(log_params):
        try:
            return m.cost_log_params(log_params)
        except Utility.SloppyCellException:
            logger.warn('Exception in cost evaluation. Cost set to inf.')
            return scipy.inf

    func = m.cost_log_params

    pmin = scipy.optimize.fmin(func, scipy.log(params),
                               *args, **kwargs)

    if isinstance(params, KeyedList):
        pout = params.copy()
        pout.update(scipy.exp(pmin))
        return pout
    else:
        return scipy.exp(pmin)

def fmin_xform(m, params, xforms, invforms, *args, **kwargs):
    """
    Nelder-Mead the cost over an arbitrary transform on the parameters.

    m         Model to minimize the cost for
    params    initial parameter estimate
    xforms    sequence of transforms (of length, len(params)) to apply to the 
              parameters before optimizing
    invforms  sequences of inverse transforms to get back to straight parameters
    *args     passed on to scipy.optimize.fmin
    **kwargs  passed on to scipy.optimize.fmin
              For information on these, consult help(scipy.optimize.fmin)
    """
    def func(xp, invforms):
        p = [inv(xp_val) for (xp_val, inv) in zip(xp, invforms)]
        try:
            return m.cost(p)
        except Utility.SloppyCellException:
            logger.warn('Exception in cost evaluation. Cost set to inf.')
            return scipy.inf

    params = scipy.array([x(xp_val) for (xp_val, x) in zip(params, xforms)])
    pmin = scipy.optimize.fmin(func, params, args = (invforms,),
                               *args, **kwargs)

    pmin = [inv(xp_val) for (xp_val, inv) in zip(pmin, invforms)]
    if isinstance(params, KeyedList):
        pout = params.copy()
        pout.update(pmin)
        return pout
    else:
        return pmin

def leastsq_log_params(m, params, *args, **kwargs):
    func = m.res_log_params

    pmin, msg = scipy.optimize.leastsq(func, scipy.log(params), *args, **kwargs)

    if isinstance(params, KeyedList):
        pout = params.copy()
        pout.update(scipy.exp(pmin))
        return pout
    else:
        return scipy.exp(pmin)
