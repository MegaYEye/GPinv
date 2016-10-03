import numpy as np
import unittest
import tensorflow as tf
import GPflow
import GPinv

class test_vgp(unittest.TestCase):
    def setUp(self):
        rng = np.random.RandomState(0)
        self.X = np.linspace(0.,1.,20)
        self.Y = np.sin(3.*self.X) + rng.randn(20)*0.1

    def test_build(self):
        m = GPinv.stvgp.StVGP(self.X.reshape(-1,1), self.Y.reshape(-1,1),
                    GPinv.kernels.RBF(1,output_dim=1),
                    GPinv.likelihoods.Gaussian())
        m._compile()

    def test_optimize(self):
        # reference GPR
        m_ref = GPflow.gpr.GPR(
                    self.X.reshape(-1,1),
                    self.Y.reshape(-1,1),
                    kern = GPflow.kernels.RBF(1))
        rslt_ref = m_ref.optimize()
        # tested StVGP
        tf.set_random_seed(1)
        m = GPinv.stvgp.StVGP(self.X.reshape(-1,1), self.Y.reshape(-1,1),
                    kern = GPinv.kernels.RBF(1,output_dim=1),
                    likelihood=GPinv.likelihoods.Gaussian())
        trainer = tf.train.AdamOptimizer(learning_rate=0.002)
        # first optimize by scipy
        m.optimize()
        # Stochastic optimization by tf.train
        rslt = m.optimize(trainer, maxiter=3000)
        print(rslt['fun'], rslt_ref['fun'])
        self.assertTrue(np.allclose(rslt['fun'], rslt_ref['fun'], atol=0.5))
        print(m.kern)
        print(m_ref.kern)
        print(m.likelihood)
        print(m_ref.likelihood)
        self.assertTrue(np.allclose(
            m.kern.lengthscales.value, m_ref.kern.lengthscales.value, rtol=0.2))
        self.assertTrue(np.allclose(
            m.kern.variance.value, m_ref.kern.variance.value, rtol=0.4))
        self.assertTrue(np.allclose(
            m.likelihood.variance.value, m_ref.likelihood.variance.value, rtol=0.2))
        # test prediction
        Xnew = np.linspace(0.,1.,22)
        mu, var = m.predict_f(Xnew.reshape(-1,1))
        mu_ref, var_ref = m_ref.predict_f(Xnew.reshape(-1,1))
        print(mu.flatten())
        print(mu_ref.flatten())
        print(var.flatten())
        print(var_ref.flatten())
        self.assertTrue(np.allclose(mu, mu_ref, atol=0.01))
        self.assertTrue(np.allclose(var, var_ref, atol=0.001))



if __name__ == '__main__':
    unittest.main()