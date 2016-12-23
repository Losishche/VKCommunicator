#!/usr/bin/env python3

__author__ = 'grishaev'

import sys
import argparse
import re
import os
import os.path
from PyQt4.QtGui import *
from PyQt4.Qt import *
from pybrain.datasets import ClassificationDataSet
from pybrain.structure.modules import SigmoidLayer, SoftmaxLayer, LinearLayer
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.supervised.trainers import RPropMinusTrainer


def init_brain(learn_data, epochs, TrainerClass=BackpropTrainer):
    if learn_data is None:
        return None
    print ("Building network")
    # net = buildNetwork(64 * 64, 8 * 8, 5, hiddenclass=TanhLayer)
    # net = buildNetwork(64 * 64, 32 * 32, 8 * 8, 5)
    net = buildNetwork(64 * 64, 5, hiddenclass=LinearLayer)
    # fill dataset with learn data
    trans = {
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'Z': 4
    }
    ds = ClassificationDataSet(4096, nb_classes=5, class_labels=['A', 'B', 'C', 'D', 'Z'])
    for inp, out in learn_data:
        ds.appendLinked(inp, [trans[out]])
    ds.calculateStatistics()
    print ("\tNumber of classes in dataset = {0}".format(ds.nClasses))
    print ("\tOutput in dataset is ", ds.getField('target').transpose())
    ds._convertToOneOfMany(bounds=[0, 1])
    print ("\tBut after convert output in dataset is \n", ds.getField('target'))
    trainer = TrainerClass(net, verbose=True)
    trainer.setData(ds)
    print("\tEverything is ready for learning.\nPlease wait, training in progress...")
    trainer.trainUntilConvergence(maxEpochs=epochs)
    print("\tOk. We have trained our network.")
    return net


def loadData(dir_name):
    list_dir = os.listdir(dir_name)
    list_dir.sort()
    list_for_return = []
    print ("Loading data...")
    for filename in list_dir:
        out = [None, None]
        print("Working at {0}".format(dir_name + filename))
        print("\tTrying get letter name.")
        lett = re.search("\w+_(\w)_\d+\.png", dir_name + filename)
        if lett is None:
            print ("\tFilename not matches pattern.")
            continue
        else:
            print("\tFilename matches! Letter is '{0}'. Appending...".format(lett.group(1)))
            out[1] = lett.group(1)
        print("\tTrying get letter picture.")
        out[0] = get_data(dir_name + filename)
        print("\tChecking data size.")
        if len(out[0]) == 64 * 64:
            print("\tSize is ok.")
            list_for_return.append(out)
            print("\tInput data appended. All done!")
        else:
            print("\tData size is wrong. Skipping...")
    return list_for_return


def get_data(png_file):
    img = QImage(64, 64, QImage.Format_RGB32)
    data = []
    if img.load(png_file):
        for x in range(64):
            for y in range(64):
                data.append(qGray(img.pixel(x, y)) / 255.0)
    else:
        print ("img.load({0}) failed!".format(png_file))
    return data


def work_brain(net, inputs):
    rez = net.activate(inputs)
    idx = 0
    data = rez[0]
    for i in range(1, len(rez)):
        if rez[i] > data:
            idx = i
            data = rez[i]
    return (idx, data, rez)


def test_brain(net, test_data):
    for data, right_out in test_data:
        out, rez, output = work_brain(net, data)
        print ("For '{0}' our net said that it is '{1}'. Raw = {2}".format(right_out, "ABCDZ"[out], output))
    pass


def main():
    app = QApplication([])
    p = argparse.ArgumentParser(description='PyBrain example')
    p.add_argument('-l', '--learn-data-dir', default="./learn", help="Path to dir, containing learn data")
    p.add_argument('-t', '--test-data-dir', default="./test", help="Path to dir, containing test data")
    p.add_argument('-e', '--epochs', default="1000", help="Number of epochs for teach, use 0 for learning until convergence")
    args = p.parse_args()
    learn_path = os.path.abspath(args.learn_data_dir) + "/"
    test_path = os.path.abspath(args.test_data_dir) + "/"
    if not os.path.exists(learn_path):
        print("Error: Learn directory not exists!")
        sys.exit(1)
    if not os.path.exists(test_path):
        print("Error: Test directory not exists!")
        sys.exit(1)
    learn_data = loadData(learn_path)
    test_data = loadData(test_path)
    # net = init_brain(learn_data, int(args.epochs), TrainerClass=RPropMinusTrainer)
    net = init_brain(learn_data, int(args.epochs), TrainerClass=BackpropTrainer)
    print ("Now we get working network. Let's try to use it on learn_data.")
    print("Here comes a tests on learn-data!")
    test_brain(net, learn_data)
    print("Here comes a tests on test-data!")
    test_brain(net, test_data)
    return 0

if __name__ == "__main__":
    sys.exit(main())