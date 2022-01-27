#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 level1c4pps developers
#
# This file is part of level1c4pps
#
# level1c4pps is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# level1c4pps is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with level1c4pps.  If not, see <http://www.gnu.org/licenses/>.
# Author(s):

#   Stephan Finkensieper <stephan.finkensieper@dwd.de>
#   Nina Hakansson <nina.hakansson@smhi.se>

"""Unit tests for the gac2pps_lib module."""

import datetime as dt
import unittest
try:
    from unittest import mock
except ImportError:
    import mock
from satpy import Scene

import level1c4pps.mersi22pps_lib as mersi22pps


class TestMersi22PPS(unittest.TestCase):
    """Test mersi22pps_lib."""

    def setUp(self):
        """Create a test scene."""
        mersi22pps.BANDNAMES = ['3', '24']
        vis006 = mock.MagicMock(attrs={'name': 'image0',
                                       'wavelength': [1, 2, 3, 'um'],
                                       'id_tag': 'ch_r06'})
        ir_108 = mock.MagicMock(attrs={'name': 'image1',
                                       'id_tag': 'ch_tb11',
                                       'wavelength': [1, 2, 3, 'um'],
                                       'start_time': dt.datetime(2009, 7, 1, 12, 1, 0),
                                       'end_time': dt.datetime(2009, 7, 1, 12, 1, 0),
                                       'platform_name': 'fy3d',
                                       'orbit_number': 99999})
        satzenith = mock.MagicMock(attrs={'name': 'satzenith',
                                          'id_tag': 'satzenith'})
        self.scene = Scene()
        scene_dict = {'3': vis006, '24': ir_108, 'satzenith': satzenith}
        for key in scene_dict:
            pps_name = scene_dict[key].attrs['name']
            self.scene[key] = scene_dict[key]
            self.scene[key].attrs['name'] = pps_name
        self.scene.attrs['sensor'] = ['mersi2']

    def test_get_encoding(self):
        """Test encoding for MERSI-2."""
        enc_exp_angles = {'dtype': 'int16',
                          'scale_factor': 0.01,
                          'zlib': True,
                          'complevel': 4,
                          '_FillValue': -32767,
                          'add_offset': 0.0}
        encoding_exp = {
            'image0': {'dtype': 'int16',
                       'scale_factor': 0.01,
                       'zlib': True,
                       'complevel': 4,
                       '_FillValue': -32767,
                       'add_offset': 0.0},
            'image1': {'dtype': 'int16',
                       'scale_factor': 0.01,
                       '_FillValue': -32767,
                       'zlib': True,
                       'complevel': 4,
                       'add_offset': 273.15},
            'satzenith': enc_exp_angles
        }
        encoding = mersi22pps.get_encoding_mersi2(self.scene)
        self.assertDictEqual(encoding, encoding_exp)

    def test_compose_filename(self):
        """Test compose filename for MERSI-2."""
        start_time = dt.datetime(2009, 7, 1, 12, 15)
        end_time = dt.datetime(2009, 7, 1, 12, 30)
        scene = mock.MagicMock(attrs={'start_time': start_time,
                                      'end_time': end_time,
                                      'orbit_number': '99999',
                                      'platform': 'Noaa19'})
        start_time = dt.datetime(2009, 7, 1, 12, 16)
        end_time = dt.datetime(2009, 7, 1, 12, 27)
        band = mock.MagicMock(attrs={'start_time': start_time,
                                     'end_time': end_time})
        fname_exp = '/out/path/S_NWC_mersi2_noaa19_99999_20090701T1216000Z_20090701T1227000Z.nc'
        fname = mersi22pps.compose_filename(scene, '/out/path', 'mersi2', band=band)
        self.assertEqual(fname, fname_exp)

    def test_set_header_and_band_attrs(self):
        """Test to set header_and_band_attrs."""
        mersi22pps.set_header_and_band_attrs(self.scene, orbit_n='12345')
        self.assertTrue(isinstance(self.scene.attrs['orbit_number'], int))
        self.assertEqual(self.scene.attrs['orbit_number'], 12345)


def suite():
    """Create the test suite for test_mersi22pps."""
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestMersi22PPS))

    return mysuite
