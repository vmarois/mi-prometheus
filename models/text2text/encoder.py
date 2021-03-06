#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Copyright (c) 2017 Sean Robertson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------------
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

"""encoder.py: Implementation of a GRU based encoder for text2text problems (e.g. translation)
    Inspiration taken from the corresponding Pytorch tutorial.
    See https://pytorch.org/tutorials/intermediate/seq2seq_translation_tutorial.html """
__author__ = "Vincent Marois "

import torch
from torch import nn
from utils.app_state import AppState

class EncoderRNN(nn.Module):
    """
    GRU Encoder for Encoder-Decoder.
    """

    def __init__(self, input_voc_size, hidden_size, bidirectional, n_layers):
        """
        Initializes an Encoder network based on a Gated Recurrent Unit.

        :param input_voc_size: size of the vocabulary set to be embedded by the Embedding layer.
        :param hidden_size: length of embedding vectors.
        :param bidirectional: indicates whether the encoder model is bidirectional or not.
        :param n_layers: number of layers for the Gated Recurrent Unit.

        """
        # call base constructor.
        super(EncoderRNN, self).__init__()

        self.hidden_size = hidden_size
        self.bidirectional = bidirectional
        self.n_layers = n_layers

        # Embedding: creates a look-up table of the embedding of a vocabulary set
        # (size: input_voc_size -> input_language.n_words) on vectors of size hidden_size.
        # adds 1 dimension to the shape of the tensor
        # WARNING: input must be of type LongTensor
        self.embedding = nn.Embedding(
            num_embeddings=input_voc_size, embedding_dim=hidden_size)

        # Apply a multi-layer gated recurrent unit (GRU) RNN to an input sequence.
        # NOTE: default number of recurrent layers is 1
        # 1st parameter: expected number of features in the input -> same as hidden_size because of embedding
        # 2nd parameter: expected number of features in hidden state -> hidden_size.
        # batch_first=True -> input and output tensors are provided as (batch, seq, feature)
        # batch_first=True do not affect hidden states
        self.gru = nn.GRU(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=self.n_layers,
            batch_first=True,
            bidirectional=self.bidirectional)

    def forward(self, input, hidden):
        """
        Runs the Encoder.

        :param input: tensor of indices, of size [batch_size x 1] (word by word looping)

        :param hidden: initial hidden state for each element in the input batch.
        Should be of size [(n_layers * n_directions) x batch_size x hidden_size]

        For every input word, the encoder outputs a vector and a hidden state, and uses the hidden state for
        the next input word.

        :return: output should be of size [batch_size x seq_len x (hidden_size * n_directions)]: tensor containing the output features h_t from the last layer of the RNN, for each t.

        :return: hidden should be of size [(n_layers * n_directions) x batch_size x hidden_size]: tensor containing the hidden state for t = seq_length.


        """
        embedded = self.embedding(input)
        # embedded: [batch_size x 1 x hidden_size]
        output = embedded

        output, hidden = self.gru(output, hidden)

        return output, hidden

    def init_hidden(self, batch_size):
        """
        Initializes the hidden states for the encoder.

        :param batch_size: batch size
        :return: initial hidden states.

        """
        if self.bidirectional:
            return torch.zeros(self.n_layers * 2, batch_size,
                               self.hidden_size).type(AppState().dtype)
        else:
            return torch.zeros(self.n_layers, batch_size,
                               self.hidden_size).type(AppState().dtype)
