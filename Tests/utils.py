#!/usr/bin/env python
# -*- coding: utf-8 -*-

import matplotlib._pylab_helpers
import matplotlib.pyplot as plt
import traceback

def CloseMatplotlib():
    """Close matplotlib scene."""
    figures=[manager.canvas.figure
         for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
    if len(figures) >= 1:
        plt.close('all')


def Close():
    """Close all scene."""
    CloseMatplotlib()


def TestFactory(Name):
    def Test(func):
        def wrapper(*args):
            try:
                func(*args)
                print(f'       {func.__name__}: {Name}.'.ljust(100) + '-'*15 + '->  PASSED')
            except Exception as error:
                print('='*50)
                print(traceback.format_exc())
                print('='*50)
                print(f'       {func.__name__}: {Name}.'.ljust(100) + '-'*15 + f'->  FAILED\n{error}')

        return wrapper
    return Test


class BaseStepTest():
    def _steps(self):
        for name in dir(self):
            if name.startswith("step"):
                yield name, getattr(self, name)

    def test_steps(self):
        for name, step in self._steps():
            try:
                step()
            except Exception as e:
                self.fail("{} failed ({}: {})".format(step, type(e), e))
