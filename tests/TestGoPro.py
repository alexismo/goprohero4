#!/usr/bin/env python

import unittest
from goprohero4 import goprohero4


class TestGoPro(unittest.TestCase):
    def setUp(self):
        # TODO
        pass

    def test_camera_init(self):
        # initialize a camera object
        camera = GoProHero4('password')
        self.assertTrue(camera is not None)
