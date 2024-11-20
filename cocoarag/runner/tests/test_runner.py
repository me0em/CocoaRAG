import pytest
from pydantic import ValidationError

import numpy as np
import numpy.typing as npt
import scipy

from cocoarag.runner.runner import Runner
from cocoarag.runner.types import RunnerConfig, TestEndPolicy


@pytest.fixture(scope="session")
def test_config() -> RunnerConfig:
    return RunnerConfig(
        thread_count=1,
        agents={"default": ""},
        test_end_policy=TestEndPolicy.END_ON_THRESHOLD_REACHED,
        threshold=0.9,
        max_iter=100,
        debug=True,
    )


@pytest.fixture(scope="session")
def test_runner(test_config) -> Runner:
    return Runner(
        config=test_config,
    )


@pytest.fixture(scope="session")
def test_points(test_runner) -> npt.NDArray[np.float64]:
    size = 10
    return test_runner._generate_synthetic_data(
        dim=4,
        num_modes=1,
        size_per_mode=size,
    )


def test_config_from_yaml() -> None:
    path = "./cocoarag/runner/tests/correct_configs.yaml"
    configs = RunnerConfig.from_yaml(path)
    assert isinstance(configs, RunnerConfig)
    # The following test should fail because some values containing in it
    # don't match the expected Pydantic model.
    path = "./cocoarag/runner/tests/incorrect_configs.yaml"
    with pytest.raises(ValidationError):
        RunnerConfig.from_yaml(path)


@pytest.mark.skip  # just because it takes time
def test_generate_synthetic_data(test_runner) -> None:
    synth_data = test_runner._generate_synthetic_data(dim=1024, num_modes=1)
    assert synth_data.shape[1] == 1024  # shape=(a, b) where b/#columns == dim


def test_get_next_points(test_runner, test_points) -> None:
    used_points_indices = np.asarray([1, 2], dtype=np.int64)
    next_points = test_runner._get_next_points(
        all_points=test_points,
        used_points_indices=used_points_indices,
    )
    assert next_points.shape[0] == test_points.shape[0] - 2


def test_integration(test_runner, test_points) -> None:
    # test_reduce_dimension
    r2_points = test_runner._reduce_dimension(points=test_points)
    assert r2_points.shape[0] == test_points.shape[0]
    assert r2_points.shape[1] == 2
    # test_estimate_density_kernel
    with pytest.raises(Exception):
        test_runner._estimate_density_kernel(
            dataset=r2_points,
        )
    kernel = test_runner._estimate_density_kernel(dataset=r2_points.T)
    assert isinstance(kernel, scipy.stats._kde.gaussian_kde)
    assert kernel.d == r2_points.T.shape[0]
    assert kernel.n == r2_points.T.shape[1]
    # test_pdf
    x_min, x_max = np.min(r2_points[:, 0]), np.max(r2_points[:, 0])
    y_min, y_max = np.min(r2_points[:, 1]), np.max(r2_points[:, 1])
    X, Y, Z = test_runner._pdf(
        kernel=kernel,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
    )
    epsilon = 0.0001
    integral = kernel.integrate_box(
        np.array([-np.inf, -np.inf]), np.array([np.inf, np.inf])
    )
    assert 1 - integral < epsilon  # integral of PDF == 1
    maximum, neighbors = test_runner._acquire_pdf_maximum(
        X=X, Y=Y, Z=Z, all_points=r2_points, radius=2, type="circle"
    )
    print(maximum, np.argmax(Z))
