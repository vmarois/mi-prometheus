#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) IBM Corporation 2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""reverse_recall.py: Spatial NOT manipulation problem"""
__author__ = "Tomasz Kornuta, Younes Bouhadjar"

import torch
import numpy as np
from problems.problem import DataTuple
from problems.seq_to_seq.algorithmic.algorithmic_seq_to_seq_problem import AlgorithmicSeqToSeqProblem, AlgSeqAuxTuple


class ManipulationSpatialNot(AlgorithmicSeqToSeqProblem):
    """
    Class generating sequences of random bit-patterns with inverted targets, so
    the system is supposed to learn NOT logical operation.
    """

    def __init__(self, params):
        """
        Constructor - stores parameters. Calls parent class initialization.

        :param params: Dictionary of parameters.
        """
        # Call parent constructor - sets e.g. the loss function, dtype.
        # Additionally it extracts "standard" list of parameters for
        # algorithmic tasks, like batch_size, numbers of bits, sequences etc.

        super(ManipulationSpatialNot, self).__init__(params)

        assert self.control_bits >= 2, "Problem requires at least 2 control bits (currently %r)" % self.control_bits
        assert self.data_bits >= 2, "Problem requires at least 1 data bit (currently %r)" % self.data_bits

    def generate_batch(self):
        """
        Generates a batch  of size [BATCH_SIZE, 2*SEQ_LENGTH+2,
        CONTROL_BITS+DATA_BITS]. Additional elements of sequence are  start and
        stop control markers, stored in additional bits.

        : returns: Tuple consisting of: input [BATCH_SIZE, 2*SEQ_LENGTH+2, CONTROL_BITS+DATA_BITS],
        output [BATCH_SIZE, 2*SEQ_LENGTH+2, DATA_BITS],
        mask [BATCH_SIZE, 2*SEQ_LENGTH+2]

        TODO: every item in batch has now the same seq_length.

        """
        # Set sequence length
        seq_length = np.random.randint(
            self.min_sequence_length, self.max_sequence_length + 1)

        # Generate batch of random bit sequences [BATCH_SIZE x SEQ_LENGTH X
        # DATA_BITS]
        bit_seq = np.random.binomial(
            1, self.bias, (self.batch_size, seq_length, self.data_bits))

        # Generate input:  [BATCH_SIZE, 2*SEQ_LENGTH+2, CONTROL_BITS+DATA_BITS]
        inputs = np.zeros([self.batch_size,
                           2 * seq_length + 2,
                           self.control_bits + self.data_bits],
                          dtype=np.float32)
        # Set start control marker.
        inputs[:, 0, 0] = 1  # Memorization bit.
        # Set bit sequence.
        inputs[:, 1:seq_length + 1,
               self.control_bits:self.control_bits + self.data_bits] = bit_seq
        # Set end control marker.
        inputs[:, seq_length + 1, 1] = 1  # Recall bit.

        # Generate target:  [BATCH_SIZE, 2*SEQ_LENGTH+2, DATA_BITS] (only data
        # bits!)
        targets = np.zeros([self.batch_size, 2 * seq_length + 2,
                            self.data_bits], dtype=np.float32)
        # Set target bit sequence - logical not.
        targets[:, seq_length + 2:, :] = np.logical_not(bit_seq)

        # Generate target mask: [BATCH_SIZE, 2*SEQ_LENGTH+2]
        mask = torch.zeros([self.batch_size, 2 * seq_length + 2]
                           ).type(torch.ByteTensor)
        mask[:, seq_length + 2:] = 1

        # PyTorch variables.
        ptinputs = torch.from_numpy(inputs).type(self.dtype)
        pttargets = torch.from_numpy(targets).type(self.dtype)

        # Return tuples.
        data_tuple = DataTuple(ptinputs, pttargets)
        aux_tuple = AlgSeqAuxTuple(mask, seq_length, 1)

        return data_tuple, aux_tuple

    # method for changing the maximum length, used mainly during curriculum
    # learning
    def set_max_length(self, max_length):
        self.max_sequence_length = max_length


if __name__ == "__main__":
    """ Tests sequence generator - generates and displays a random sample"""

    # "Loaded parameters".
    from utils.param_interface import ParamInterface 
    params = ParamInterface()
    params.add_custom_params({'control_bits': 2,
                              'data_bits': 8,
                              'batch_size': 1,
                              'min_sequence_length': 1,
                              'max_sequence_length': 10})
    # Create problem object.
    problem = ManipulationSpatialNot(params)
    # Get generator
    generator = problem.return_generator()
    # Get batch.
    data_tuple, aux_tuple = next(generator)
    # Display single sample (0) from batch.
    problem.show_sample(data_tuple, aux_tuple)
