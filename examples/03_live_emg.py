# The MIT License (MIT)
#
# Copyright (c) 2017 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

from __future__ import print_function
from matplotlib import pyplot as plt
import collections
import myo
import numpy as np
import threading
import time


class Listener(myo.DeviceListener):

  def __init__(self, queue_size=8):
    self.lock = threading.Lock()
    self.emg_data_queue = collections.deque(maxlen=queue_size)

  def on_connected(self, event):
    event.device.stream_emg(True)

  def on_emg(self, event):
    with self.lock:
      self.emg_data_queue.append((event.timestamp, event.emg))

  def get_emg_data(self):
    with self.lock:
      return list(self.emg_data_queue)


def main():
  queue_size = 512

  # Initialize Myo and create a Hub and our listener.
  myo.init()
  hub = myo.Hub()
  listener = Listener(queue_size)

  # Create the axes for the plot.
  fig = plt.figure()
  axes = [fig.add_subplot('81' + str(i)) for i in range(1, 9)]
  [(ax.set_ylim([-100, 100])) for ax in axes]
  graphs = [ax.plot(np.arange(queue_size), np.zeros(queue_size))[0] for ax in axes]
  plt.ion()

  def plot_main():
    emgs = np.array([x[1] for x in listener.get_emg_data()]).T
    for g, data in zip(graphs, emgs):
      if len(data) < queue_size:
        data = np.concatenate([np.zeros(queue_size - len(data)), data])
      g.set_ydata(data)
    plt.draw()

  try:
    threading.Thread(target=lambda: hub.run_forever(listener.on_event)).start()
    while True:
      plot_main()
      plt.pause(1.0 / 30)
  finally:
    hub.stop()  # Will also stop the thread


if __name__ == '__main__':
  main()
