#!/usr/bin/env python3

# Author: Anshuman Khaund <ansh.khaund@gmail.com>

import sys
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import plots


class OutputPCA:
    """ Returns,
        1. Pareto-chart of the explained variance, or
        2. Low-dimensional (2D or 3D) projection of the data, or
        3. The principal components on which to project the data.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        # Data columns being standardized prior to PCA
        df = pd.DataFrame(data=StandardScaler().fit_transform(df.values),
                          columns=df.columns,
                          index=df.index)
        self._df = df
        self._pca = PCA().fit(df.values)

    def get_explained_variance(self):
        """ Pareto-Chart of the explained variance
        """
        expl_var = pd.DataFrame({
            "var_exp": self._pca.explained_variance_ratio_,
            "cumul_var_exp": self._pca.explained_variance_ratio_.cumsum()
        })
        expl_var.index += 1
        fig = plots.explained_variance_plot(
            df=expl_var,
            x_title="Principal Component Rank",
            y_title="Variance Explained",
            title="Variance explained by Principal Components"
        )
        return fig

    def get_scree_plot(self):
        eig_vals = pd.DataFrame({
            "eig_val": self._pca.explained_variance_
        })
        eig_vals.index += 1
        fig = plots.scree_plot(
            df=eig_vals,
            x_title="Principal Component rank",
            y_title="Eigen Value",
            title="Eigen Values by Principal Components")
        return fig

    def get_projections(self,
                        labels,
                        n_components: int = 2,
                        feature_projections: bool = True):
        """ Low-dimensional (2D or 3D) projection of the data
        """
        features, indeces = self._df.columns, self._df.index.values
        n = n_components
        # input checks
        if n_components not in {2, 3}:
            print("\033[1m"
                  "Input Error for 'visualize' function. \n"
                  "\033[0m"
                  f"Given: {n_components=}. It must be 2 or 3. \n",
                  file=sys.stderr)
            return
        pca_components = pd.DataFrame(
            data=self._pca.components_[:n, :].T,  # components are as rows
            index=features,
            columns=["PC" + str(i + 1) for i in range(n)]
        )
        pca_transformed = pd.DataFrame(
            data=np.concatenate(
                (self._pca.transform(self._df.values)[:, :n],
                 labels.reshape(len(labels), 1),
                 indeces.reshape(len(indeces), 1)),
                axis=1),
            columns=list(pca_components.columns) + ["label", "idx"]
        )
        fig = plots.low_dimensional_projection(
            n,
            pca_components,
            pca_transformed,
            feature_projections,
            title="Principal Component Analysis"
        )
        return fig

    def get_components(self,
                       n_components: int = 2):
        """ The principal components on which to project the data
        """
        print("Principal components returned as 'rows'.")
        return self._pca.components_[:n_components, :]


# Test
if __name__ == "__main__":

    from sklearn import datasets

    # test PCA
    iris = datasets.load_iris()
    iris.target = (pd.Series(iris.target)
                   .replace(dict(zip(np.unique(iris.target),
                                     iris.target_names)))
                   .values)
    iris.data = pd.DataFrame(
        data=iris.data,
        columns=iris.feature_names
    )
    # 2D visualization
    OutputPCA(iris.data).get_projections(
        labels=iris.target,
        project_features=True
    ).show()
    # 3D visualization
    OutputPCA(iris.data).get_projections(
        labels=iris.target,
        n_components=3
    ).show()
    # Scree Plot
    OutputPCA(iris.data).get_scree_plot().show()
    # Explained variance
    OutputPCA(iris.data).get_explained_variance().show()
    # Get components
    OutputPCA(iris.data).get_components(n_components=3)
