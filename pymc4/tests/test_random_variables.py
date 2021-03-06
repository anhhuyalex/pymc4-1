"""
Tests for PyMC4 random variables
"""
import pytest
from .. import _random_variables


def tfp_supported_args():
    """Provide arguments for each supported Tensorflow distribution"""
    _tfp_supported_args = (
        (_random_variables.Bernoulli, {"probs": 0.5}),
        (_random_variables.Beta, {"concentration0": 1, "concentration1": 1}),
        (_random_variables.Binomial, {"total_count": 5.0, "probs": 0.5, "sample": 1}),
        (_random_variables.Categorical, {"probs": [0.1, 0.5, 0.4]}),
        (_random_variables.Cauchy, {"loc": 0, "scale": 1}),
        (_random_variables.Chi2, {"df": 2}),
        (_random_variables.Dirichlet, {"concentration": [1, 2], "sample": [0.5, 0.5]}),
        (_random_variables.Exponential, {"rate": 1}),
        (_random_variables.Gamma, {"concentration": 3.0, "rate": 2.0}),
        (_random_variables.Geometric, {"probs": 0.5, "sample": 10}),
        (_random_variables.Gumbel, {"loc": 0, "scale": 1}),
        (_random_variables.HalfCauchy, {"loc": 0, "scale": 1}),
        (_random_variables.HalfNormal, {"scale": 3.0}),
        (_random_variables.InverseGamma, {"concentration": 3, "rate": 2}),
        (_random_variables.InverseGaussian, {"loc": 1, "concentration": 1}),
        (_random_variables.Kumaraswamy, {"concentration0": 0.5, "concentration1": 0.5}),
        (_random_variables.LKJ, {"dimension": 1, "concentration": 1.5, "sample": [[1]]}),
        (_random_variables.Laplace, {"loc": 0, "scale": 1}),
        (_random_variables.LogNormal, {"loc": 0, "scale": 1}),
        (_random_variables.Logistic, {"loc": 0, "scale": 3}),
        (
            _random_variables.Multinomial,
            {"total_count": 4, "probs": [0.2, 0.3, 0.5], "sample": [1, 1, 2]},
        ),
        (
            _random_variables.MultivariateNormalFullCovariance,
            {"loc": [1, 2], "covariance_matrix": [[0.36, 0.12], [0.12, 0.36]], "sample": [1, 2]},
        ),
        (_random_variables.NegativeBinomial, {"total_count": 5, "probs": 0.5, "sample": 5}),
        (_random_variables.Normal, {"loc": 0, "scale": 1}),
        (_random_variables.Pareto, {"concentration": 1, "scale": 0.1, "sample": 5}),
        (_random_variables.Poisson, {"rate": 2}),
        (_random_variables.StudentT, {"loc": 0, "scale": 1, "df": 10}),
        (_random_variables.Triangular, {"low": 0.0, "high": 1.0, "peak": 0.5}),
        (_random_variables.Uniform, {"low": 0, "high": 1}),
        (_random_variables.VonMises, {"loc": 0, "concentration": 1}),
        (_random_variables.Wishart, {"df": 3, "scale_tril": [[1]], "sample": [[1]]}),
    )

    ids = [dist[0].__name__ for dist in _tfp_supported_args]
    return {"argnames": ("randomvariable", "kwargs"), "argvalues": _tfp_supported_args, "ids": ids}


def test_tf_session_cleared(tf_session):
    """Check that fixture is finalizing correctly"""
    assert len(tf_session.graph.get_operations()) == 0


@pytest.mark.parametrize(**tfp_supported_args())
def test_rvs_logp_and_forward_sample(tf_session, randomvariable, kwargs):
    """Test all RandomVariables that are implemented with TFP distributions"""
    sample = kwargs.pop("sample", 0.1)
    dist = randomvariable("test_dist", **kwargs, validate_args=True)

    if randomvariable.__name__ != "Binomial":
        # Assert that values are returned with no exceptions
        log_prob = dist.log_prob()
        vals = tf_session.run([log_prob], feed_dict={dist._backend_tensor: sample})
        assert vals is not None

    else:
        # TFP issue ticket for Binom.sample_n https://github.com/tensorflow/probability/issues/81
        assert randomvariable.__name__ == "Binomial"
        with pytest.raises(NotImplementedError) as err:
            dist.log_prob()
            assert "NotImplementedError: sample_n is not implemented: Binomial" == str(err)
