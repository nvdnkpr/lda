from __future__ import absolute_import, division, unicode_literals  # noqa

import io
import os

import numpy as np
import oslotest.base

import lda.utils as utils


class TestUtils(oslotest.base.BaseTestCase):

    np.random.seed(99)

    D = 100
    W = 50
    N_WORDS_PER_DOC = 500
    N = W * N_WORDS_PER_DOC
    dtm = np.zeros((D, W), dtype=int)
    for d in range(D):
        dtm[d] = np.random.multinomial(N_WORDS_PER_DOC, np.ones(W) / W)
    N_BY_W = np.sum(dtm, axis=0)
    N_BY_D = np.sum(dtm, axis=1)

    def test_setup(self):
        dtm, D, N_WORDS_PER_DOC = self.dtm, self.D, self.N_WORDS_PER_DOC
        self.assertEqual(np.sum(dtm), D * N_WORDS_PER_DOC)

    def test_matrix_to_lists(self):
        dtm, D, N_WORDS_PER_DOC = self.dtm, self.D, self.N_WORDS_PER_DOC
        N_BY_D, N_BY_W = self.N_BY_D, self.N_BY_W
        WS, DS = utils.matrix_to_lists(dtm)
        self.assertEqual(len(WS), D * N_WORDS_PER_DOC)
        self.assertEqual(len(WS), len(DS))
        self.assertEqual(dtm.shape, (max(DS) + 1, max(WS) + 1))
        self.assertTrue(all(DS == sorted(DS)))
        self.assertTrue(np.all(np.bincount(DS) == N_BY_D))
        self.assertTrue(np.all(np.bincount(WS) == N_BY_W))

    def test_lists_to_matrix(self):
        dtm = self.dtm
        WS, DS = utils.matrix_to_lists(dtm)
        dtm_new = utils.lists_to_matrix(WS, DS)
        self.assertTrue(np.all(dtm == dtm_new))

    def test_ldac2dtm_offset(self):
        test_dir = os.path.dirname(__file__)
        reuters_ldac_fn = os.path.join(test_dir, 'reuters.ldac')
        self.assertRaises(ValueError, utils.ldac2dtm, open(reuters_ldac_fn), offset=1)

    def test_ldac2dtm(self):
        test_dir = os.path.dirname(__file__)
        reuters_ldac_fn = os.path.join(test_dir, 'reuters.ldac')
        dtm = utils.ldac2dtm(open(reuters_ldac_fn))
        self.assertEqual(dtm.shape, (395, 4258))
        self.assertEqual(dtm.sum(), 84010)

    def test_ldac_conversion(self):
        dtm = self.dtm
        N, V = dtm.shape
        doclines = list(utils.dtm2ldac(self.dtm))
        nd_unique = np.sum(dtm > 0, axis=1)
        for n, docline in zip(nd_unique, doclines):
            self.assertEqual(n, int(docline.split(' ')[0]))
        self.assertEqual(len(doclines), N)
        f = io.StringIO('\n'.join(doclines))
        dtm_new = utils.ldac2dtm(f)
        self.assertTrue(np.all(dtm == dtm_new))
