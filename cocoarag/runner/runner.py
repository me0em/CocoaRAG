from decimal import Decimal
from typing import Any, Literal
from uuid import uuid4, UUID

from pydantic import BaseModel, Field

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import seaborn as sns
import scipy
import umap

from .types import RunnerConfig, Result


class Runner(BaseModel):
    """
    Runner represents the execution manager that runs experiments. It
    orchestrates the different steps in evaluating the agent.
    """

    # NOTE: Keep in mind to change the types in the typedef in the
    # init in case that this is changing here in the future.
    _dtype: npt.DTypeLike = np.float64
    config: RunnerConfig
    id: UUID = uuid4()
    score: float | None = 0
    _results: list[Result] | None = None
    used_points_indices: npt.NDArray[np.int64] = Field(
        default_factory=lambda: np.empty((0), dtype=np.int64)
    )

    class Config:
        arbitrary_types_allowed = True

    @property
    def info(self) -> dict[str, Any]:
        return {"id": self.id}

    def get_embeddings(self) -> npt.NDArray[_dtype]:
        raise NotImplementedError

    def _generate_synthetic_data(
        self,
        min: int = -10,
        max: int = 10,
        num_modes: int = 30,
        size_per_mode: int | None = None,
        dim: int = 2,
    ) -> npt.NDArray[_dtype]:
        """
        Generates synthetic dim dimensional random points that are normally
        distributed.

        Args:
            `min`: The min values for the x components of individual
            distributions.\n
            `max`: The max values for the y components of individual
            distributions.\n
            `limit_y`: The max and min values for the y components of
            individual distributions.\n
            `num_modes`: The number of modes/centers for individual
            distributions.\n
            `size_per_mode`: The number of points per mode.\n
            should have a fixed amount of points.\n
        Returns:
            A (k, 2) shaped np.array containing the points generated.
        """
        points = []
        centers = np.random.uniform(min, max, (num_modes, dim))
        for i in range(num_modes):
            if size_per_mode is None:
                size_per_mode = np.random.randint(10, 50)
            mode_points = np.random.normal(
                loc=centers[i],
                scale=np.random.uniform(0.1, 0.9, dim),
                size=(size_per_mode, dim),
            )
            points.append(mode_points)
        return np.vstack(points)

    def _get_next_points(
        self,
        all_points: npt.NDArray[_dtype],
        used_points_indices: npt.NDArray[np.int64],
    ) -> npt.NDArray[_dtype]:
        """
        Calculates what are the next points that are going to be in the next
        iteration.

        Args:
            `all_points`: The set of points that we consider.
            `used_points_indices`: The points that were used.

        Returns:
            The next to be evaluated pdf upon.
        """
        self.used_points_indices = np.concatenate(
            (self.used_points_indices, used_points_indices), dtype=np.int64
        )
        return np.delete(all_points, self.used_points_indices, axis=0)

    def _reduce_dimension(self, points: npt.NDArray[_dtype]) -> npt.NDArray[_dtype]:
        """
        Performs non-linear dimension reduction on points from the embedding
        space to a lower representational space.\n
        Why? It's more convenient to perform optimization on and allow for
        visual representation of the probability distribution function
        estimates.

        Args:
            `points`: the points from R^n.

        Returns:
            The transformed points in R^2.
        """
        reducer = umap.UMAP(n_components=2)
        transformed_points = reducer.fit_transform(points)
        return np.array(transformed_points, dtype=self._dtype)

    def _estimate_density_kernel(
        self,
        dataset: npt.NDArray[_dtype],
        bw_method: Literal["scott", "silverman"] | None = "scott",
        weights: npt.NDArray[_dtype] | None = None,
    ) -> scipy.stats.gaussian_kde:
        """
        Estimates a Gaussian density kernel, fitted with a given
        set of points.

        Args:
            `dataset`: The data that fits the kernel. It should be of
            shape (2, k).\n
            `bw_method`: Bandwidth method to used.\n
            `weights`: The weights for each index (if any).
        Returns:
            A fitted Gaussian kernel
        """
        assert dataset.shape[0] == 2, "The shape should be (2, num_points)"
        return scipy.stats.gaussian_kde(
            dataset=dataset,
            bw_method=bw_method,
            weights=weights,
        )

    def _pdf(
        self,
        kernel: scipy.stats.gaussian_kde,
        x_min: np.float64,
        y_min: np.float64,
        x_max: np.float64,
        y_max: np.float64,
    ) -> tuple[npt.NDArray[_dtype], npt.NDArray[_dtype], npt.NDArray[_dtype]]:
        """
        Calculates a surface area that basically integrates to 1

        Args:
            `kernel`: A Gaussian kernel.\n
            `x_min`: The minimum x component.\n
            `y_min`: The minimum y component.\n
            `x_max`: The maximum x component.\n
            `y_max`: The maximum y component.\n
        Returns:
            A tuple containing the meshgrid X, Y and the surface Z.
        """
        _spread = 5
        X, Y = np.mgrid[
            x_min - _spread : x_max + _spread : 100j,
            y_min - _spread : y_max + _spread : 100j,
        ]
        positions = np.vstack([X.ravel(), Y.ravel()])
        Z = np.reshape(kernel(positions).T, X.shape)
        return X, Y, Z

    def _get_point_neighbors(
        self,
        point: npt.NDArray[_dtype],
        all_points: npt.NDArray[_dtype],
        radius: float | int = 0.5,
        limit: int | None = None,
        type: Literal["circle", "rectangle"] = "circle",
    ) -> npt.NDArray[_dtype]:
        """
        Calculates and returns the neighbors points for a given point

        Args:
            `point`: The point for which we are calculatng the neighbors.
            `all_points`: The points of the data that induced the KDE. It should
            be specified if `with_neighbors` is True.\n
            `radius`: The radius inside of which a point is
            considered neighbor of the maximum value.\n
            `limit`: If specified, it returns up to this limit value
            neighbors.\n
            `type`: Whether to consider rectangular or circle neighborhood.\n
        Returns:
            The neighbors as np.array.
        """
        if type == "circle":
            squared_distance = np.sum((all_points - point) ** 2, axis=1)
            neighbors = all_points[squared_distance <= radius**2]
        elif type == "rectangle":
            x_max, y_max = np.max(all_points[:, 0]), np.max(all_points[:, 1])
            condition = (
                (all_points[:, 0] >= x_max - radius)
                & (all_points[:, 0] <= x_max + radius)
                & (all_points[:, 1] >= y_max - radius)
                & (all_points[:, 1] <= y_max + radius)
            )
            neighbors = all_points[condition]
        if limit:
            neighbors = neighbors[:limit, :]
        return neighbors

    def _acquire_pdf_maximum(
        self,
        X: npt.NDArray[_dtype],
        Y: npt.NDArray[_dtype],
        Z: npt.NDArray[_dtype],
        all_points: npt.NDArray[_dtype],
        with_neighbors: bool = True,
        radius: float = 0.5,
        limit: int | None = None,
        type: Literal["circle", "rectangle"] = "circle",
    ) -> tuple[npt.NDArray[_dtype], npt.NDArray[_dtype]]:
        """
        Returns the maximum value of the density estimation

        Args:
            `X`: X coordinates
            `Y`: Y coordinates
            `Z`: The density estimation surface.\n
            `all_points`: The points of the data that induced the KDE. It should
            be specified if `with_neighbors` is True.\n
            `with_neighbors`: If specified, it returns the neighbors of
            the maximum value.\n
            `radius`: The radius inside of which a point is
            considered neighbor of the maximum value.\n
            `limit`: If specified, it returns up to this limit value
            neighbors.\n
            `type`: Whether to consider rectangular or circle neighborhood.\n
        Returns:
            A tuple with the value of the maximum and its neighbors.
        """
        z_argmax = np.where(np.max(Z) == Z)
        x_max, y_max = X[z_argmax][0], Y[z_argmax][0]
        max_pdf = np.array([x_max, y_max])
        if with_neighbors:
            neighbors = self._get_point_neighbors(
                point=max_pdf,
                all_points=all_points,
                radius=radius,
                limit=limit,
                type=type,
            )
            return max_pdf, neighbors
        return max_pdf, np.empty((1,))

    def plot(
        self,
        points: npt.NDArray[_dtype],
        X: npt.NDArray[_dtype],
        Y: npt.NDArray[_dtype],
        Z: npt.NDArray[_dtype],
        opt: npt.NDArray[_dtype],
    ) -> None:
        _, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(16, 4))

        sns.scatterplot(x=points[:, 0], y=points[:, 1], ax=ax0)
        ax1.contour(X, Y, Z, cmap=mpl.colormaps["rocket"])
        ax1.plot(opt[0], opt[1], "x")
        sns.kdeplot(data=Z.ravel(), ax=ax2)

        ax0.set_title("Reduced-dimensional Points")
        ax1.set_title("Kernel Density Estimation of the Points")
        ax1.set_xlabel("xs")
        ax1.set_ylabel("ys")
        ax2.set_title("Weighted Densities")
        ax2.set_xlabel("values of the densities at points")
        ax2.set_ylabel("density of the densities")

    def _generate_result(self) -> Result: ...

    def _formulate_question(self) -> str: ...

    def _get_agent_response(self) -> str: ...

    def _evaluate_response(self) -> Decimal: ...

    def run(self) -> None: ...

    @property
    def results(self) -> list[Result]: ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...
