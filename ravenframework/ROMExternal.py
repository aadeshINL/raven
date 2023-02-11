# Copyright 2017 Battelle Energy Alliance, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Created on October 12, 2022

@author: cogljj

ROM Loader for serialized surrogate model (ROM) for internal usage
Unlike externalROMloader.ravenROMexternal, this assumes ravenframework is
already in the path.
"""

import os
import pickle
import numpy as np

class ROMLoader(object):
  """
    External ROM loader and user-gate
  """
  def __init__(self, binaryFileName, _whereFrameworkIs=None):
    """
      This constructor un-serializes the ROM generated by RAVEN and
      it makes the ROM available for external usage
      @ In, binaryFileName, str, the location of the serialized (pickled) ROM that needs to be imported
      @ In, _whereFrameworkIs, None, ignored
      @ Out, None
    """
    self._binaryLoc = binaryFileName
    self._load(binaryFileName)

  def _load(self, binaryFileName):
    """
      Load the ROM.
      @ In, binaryFileName, str, the location of the serialized (pickled) ROM that needs to be imported
      @ Out, None
    """
    # de-serialize the ROM
    serializedROMlocation = os.path.abspath(binaryFileName)
    if not os.path.exists(serializedROMlocation):
      raise IOError('The serialized (binary) file has not been found in location "' + str(serializedROMlocation)+'" !')
    self.rom = pickle.load(open(serializedROMlocation, mode='rb'))

  def __getstate__(self):
    """
      Deep copy.
      @ In, None
      @ Out, d, dict, self representation
    """
    d = {'binaryFileName': self._binaryLoc}
    return d

  def __setstate__(self, d):
    """
      Deep paste.
      @ In, d, dict, self representation
      @ Out, None
    """
    self._binaryLoc = d['binaryFileName']
    self._load(self._binaryLoc)

  def setAdditionalParams(self, nodes):
    """
      Set ROM parameters for external evaluation
      @ In, nodes, list, list of xml nodes for setting parameters of pickleROM
      @ Out, None
    """
    from ravenframework.SupervisedLearning.pickledROM import pickledROM
    spec = pickledROM.getInputSpecification()()
    # Changing parameters for the ROM
    for node in nodes:
      spec.parseNode(node)
    # Matching the index name of the defaul params object
    params = {'paramInput':spec}
    self.rom.setAdditionalParams(params)

  def evaluate(self,request):
    """
      Evaluate the ROM
      @ In, request, dict, dictionary of realization that needs to be evaluated {'varName':numpy.ndarray,'varName':numpy.ndarray, etc.}
      @ Out, output, list, dictionary of the outputs {'output1':np.ndarray,'output2':np.ndarray, etc.}
      the arrays have the shape (NumberOfRequestedEvaluations,)
    """
    output = []
    for index in range(len(list(request.values())[0])):
      output.append(self.rom.evaluate({k:np.asarray(v[index]) for k,v in request.items()}))
    return output

  def getInitParams(self):
    """
      Return the initialization parameter of the pickled ROM
      @ In, None
      @ Out, params, dict, dictionary of init params
    """
    return self.rom.getInitParams()
