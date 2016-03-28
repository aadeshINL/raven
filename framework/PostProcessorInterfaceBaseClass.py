"""
Created on December 1st, 2015

"""
from __future__ import division, print_function, unicode_literals, absolute_import
import warnings
warnings.simplefilter('default',DeprecationWarning)

#External Modules------------------------------------------------------------------------------------
import abc
import os
import numpy as np
#External Modules End--------------------------------------------------------------------------------

#Internal Modules------------------------------------------------------------------------------------
from cached_ndarray import c1darray
import utils
import MessageHandler
#Internal Modules End--------------------------------------------------------------------------------

class PostProcessorInterfaceBase(utils.metaclass_insert(abc.ABCMeta,object),MessageHandler.MessageUser):
  """
    This class is the base interfaced post-processor clas
    It contains the three methods that need to be implemented:
      - initialize
      - run
      - readMoreXML
  """

  def __init__(self, messageHandler):
    """
      Constructor
      @ In, messageHandler, MessageHandler, message handler object
      @ Out, None
    """
    self.type = self.__class__.__name__
    self.name = self.__class__.__name__
    self.messageHandler = messageHandler


  def initialize(self):
    """
      Method to initialize the Interfaced Post-processor. Note that the user needs to specify two mandatory variables:
       - self.inputFormat:  dataObject that the PP is supposed to receive in input
       - self.outputFormat: dataObject that the PP is supposed to generate in output
      These two variables check that the input and output dictionaries match what PP is supposed to receive and generate
      Refer to the manual on the format of these two dictionaries
      @ In, None
      @ Out, None
    """
    self.inputFormat  = None
    self.outputFormat = None

  def readMoreXML(self,xmlNode):
    """
      Function that reads elements this post-processor will use
      @ In, xmlNode, ElementTree, Xml element node
      @ Out, None
    """
    pass

  def run(self,inputDic):
    """
     Method to post-process the dataObjects
     @ In, inputDic, dict, dictionary which contains the data inside the input DataObject
     @ Out, None

    """
    pass

  def checkGeneratedDicts(self,outputDic):
    """
      Method to check that dictionary generated in def run(self, inputDic) is consistent
      @ In, outputDic, dict, dictionary generated by the run method
      @ Out, True/False, bool, outcome of the outputDic check
    """
    if self.checkOutputFormat(outputDic['data']['input']) and self.checkOutputFormat(outputDic['data']['output']):
      return True
    else:
      return False

  def checkOutputFormat(self,outputDic):
    """
      This method checks that the generated output part of the generated dictionary is built accordingly to outputFormat
      @ In, outputDic, dict, dictionary generated by the run method
      @ Out, outcome, bool, outcome of the outputDic check (True/False)
    """
    outcome = True
    if isinstance(outputDic,dict):
      if self.outputFormat == 'HistorySet' or self.outputFormat == 'History':
        for key in outputDic:
          if isinstance(outputDic[key],dict):
            outcome = outcome and True
          else:
            outcome = outcome and False
          for keys in outputDic[key]:
            if isinstance(outputDic[key][keys],(np.ndarray,c1darray)):
              outcome = outcome and True
            else:
              outcome = outcome and False
      else:
        for key in outputDic:
          if isinstance(outputDic[key],(np.ndarray,c1darray)):
            outcome = outcome and True
          else:
            outcome = outcome and False
    else:
      outcome = outcome and False
    return outcome


  def checkInputFormat(self,inputDic):
    """
      This method checks that the generated input part of the generated dictionary is built accordingly to inputFormat
      @ In, inputDic, dict, dictionary generated by the run method
      @ Out, outcome, bool, outcome of the inputDic check (True/False)
    """

    outcome = True
    if isinstance(inputDic,dict):
      for key in inputDic:
        if isinstance(inputDic[key],np.ndarray):
          outcome = outcome and True
        else:
          outcome = outcome and False
    else:
      outcome = False
    return outcome


  def checkArrayMonotonicity(time):
    """
      This method checks that an array is increasing monotonically
      @ In, time, numpy array, array to be checked
      @ Out, outcome, bool, outcome of the monotonicity check
    """
    outcome = True
    for t in time:
      if t != 0:
        if time[t] > time[t-1]:
          outcome = outcome and True
        else:
          outcome = outcome and False
    return outcome
