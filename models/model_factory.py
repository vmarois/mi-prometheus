#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""model_factory.py: Factory building models"""
from models.ntm.ntm_layer import NTM
__author__ = "Tomasz Kornuta"

class ModelFactory(object):
    """   
    Class returning concrete models depending on the name provided in the list of parameters.
    """
    
    @staticmethod
    def build_model(params):
        """ Static method returning particular model, depending on the name provided in the list of parameters.
        
        :param params: Dictionary of parameters (in particular containing 'name' which is equivalend to model name)
        :returns: Instance of a given model.
        """
        # Check name
        if 'name' not in params:
            print("Model parameter dictionary does not contain 'name'")
            raise ValueError
        # Try to load model
        name = params['name']
        if name == 'ntm_v1':
            return NTM(params)
        else:
            raise ValueError

