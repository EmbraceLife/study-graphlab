from ... import _supervised_learning as _sl
import graphlab.connect as _mt

_DEFAULT_SOLVER_OPTIONS = {
'convergence_threshold': 1e-2,
'step_size': 1.0,
'lbfgs_memory_level': 11,
'max_iterations': 10}

def submit_training_job(env, dataset, target, features=None,
    l2_penalty=0.01, l1_penalty=0.0,
    solver='auto', feature_rescaling=True,
    convergence_threshold = _DEFAULT_SOLVER_OPTIONS['convergence_threshold'],
    step_size = _DEFAULT_SOLVER_OPTIONS['step_size'],
    lbfgs_memory_level = _DEFAULT_SOLVER_OPTIONS['lbfgs_memory_level'],
    max_iterations = _DEFAULT_SOLVER_OPTIONS['max_iterations'],
    class_weights = None,
    validation_set = None):
    """
    Submit a job to create a
    :class:`~graphlab.logistic_classifier.LogisticClassifier` (using logistic
    regression as a classifier) to predict the class of a discrete target
    variable (binary or multiclass) based on a model of class probability as a
    logistic function of a linear combination of the features.  In addition to
    standard numeric and categorical types, features can also be extracted
    automatically from list or dictionary-type SFrame columns.

    This model can be regularized with an l1 penalty, an l2 penalty, or both. By
    default this model has an l2 regularization weight of 0.01.

    Parameters
    ----------
    env : graphlab.deploy.hadoop_cluster.HadoopCluster
        Hadoop cluster to submit the training job

    dataset : SFrame
        Dataset for training the model.

    target : string
        Name of the column containing the target variable. The values in this
        column must be of string or integer type. String target variables are
        automatically mapped to integers in the order in which they are provided.
        For example, a target variable with 'cat' and 'dog' as possible
        values is mapped to 0 and 1 respectively with 0 being the base class
        and 1 being the reference class. Use `model['classes']` to retrieve
        the order in which the classes are mapped.

    features : list[string], optional
        Names of the columns containing features. 'None' (the default) indicates
        that all columns except the target variable should be used as features.

        The features are columns in the input SFrame that can be of the
        following types:

        - *Numeric*: values of numeric type integer or float.

        - *Categorical*: values of type string.

        - *Array*: list of numeric (integer or float) values. Each list element
          is treated as a separate feature in the model.

        - *Dictionary*: key-value pairs with numeric (integer or float) values
          Each key of a dictionary is treated as a separate feature and the
          value in the dictionary corresponds to the value of the feature.
          Dictionaries are ideal for representing sparse data.

        Columns of type *list* are not supported. Convert such feature
        columns to type array if all entries in the list are of numeric
        types. If the lists contain data of mixed types, separate
        them out into different columns.

    l2_penalty : float, optional
        Weight on l2 regularization of the model. The larger this weight, the
        more the model coefficients shrink toward 0. This introduces bias into
        the model but decreases variance, potentially leading to better
        predictions. The default value is 0.01; setting this parameter to 0
        corresponds to unregularized logistic regression. See the ridge
        regression reference for more detail.

    l1_penalty : float, optional
        Weight on l1 regularization of the model. Like the l2 penalty, the
        higher the l1 penalty, the more the estimated coefficients shrink toward
        0. The l1 penalty, however, completely zeros out sufficiently small
        coefficients, automatically indicating features that are not useful
        for the model. The default weight of 0 prevents any features from
        being discarded. See the LASSO regression reference for more detail.

    solver : string, optional
        Name of the solver to be used to solve the regression. See the
        references for more detail on each solver. Available solvers are:

        - *auto (default)*: automatically chooses the best solver for the data
          and model parameters.
        - *newton*: Newton-Raphson
        - *lbfgs*: limited memory BFGS
        - *fista*: accelerated gradient descent

        For this model, the Newton-Raphson method is equivalent to the
        iteratively re-weighted least squares algorithm. If the l1_penalty is
        greater than 0, use the 'fista' solver.

        The model is trained using a carefully engineered collection of methods
        that are automatically picked based on the input data. The ``newton``
        method  works best for datasets with plenty of examples and few features
        (long datasets). Limited memory BFGS (``lbfgs``) is a robust solver for
        wide datasets (i.e datasets with many coefficients).  ``fista`` is the
        default solver for l1-regularized linear regression. The solvers are all
        automatically tuned and the default options should function well. See
        the solver options guide for setting additional parameters for each of
        the solvers.

        See the user guide for additional details on how the solver is chosen.
        (see `here
        <https://turi.com/learn/userguide/supervised-learning/linear-regression.html>`_)



    feature_rescaling : boolean, optional

        Feature rescaling is an important pre-processing step that ensures that
        all features are on the same scale. An l2-norm rescaling is performed
        to make sure that all features are of the same norm. Categorical
        features are also rescaled by rescaling the dummy variables that are
        used to represent them. The coefficients are returned in original scale
        of the problem. This process is particularly useful when features
        vary widely in their ranges.


    convergence_threshold : float, optional

        Convergence is tested using variation in the training objective. The
        variation in the training objective is calculated using the difference
        between the objective values between two steps. Consider reducing this
        below the default value (0.01) for a more accurately trained model.
        Beware of overfitting (i.e a model that works well only on the training
        data) if this parameter is set to a very low value.

    lbfgs_memory_level : float, optional

        The L-BFGS algorithm keeps track of gradient information from the
        previous ``lbfgs_memory_level`` iterations. The storage requirement for
        each of these gradients is the ``num_coefficients`` in the problem.
        Increasing the ``lbfgs_memory_level ``can help improve the quality of
        the model trained. Setting this to more than ``max_iterations`` has the
        same effect as setting it to ``max_iterations``.

    max_iterations : float, optional

        The maximum number of allowed passes through the data. More passes over
        the data can result in a more accurately trained model. Consider
        increasing this (the default value is 10) if the training accuracy is
        low and the *Grad-Norm* in the display is large.

    step_size : float, optional

        The starting step size to use for the ``fista`` solver. The default is
        set to 1.0, this is an aggressive setting. If the first iteration takes
        a considerable amount of time, reducing this parameter may speed up
        model training.

    class_weights : {dict, `auto`}, optional

        Weights the examples in the training data according to the given class
        weights. If set to `None`, all classes are supposed to have weight one. The
        `auto` mode set the class weight to be inversely proportional to number of
        examples in the training data with the given class.

    validation_set : SFrame, optional

        A dataset for monitoring the model's generalization performance.
        For each row of the progress table, the chosen metrics are computed
        for both the provided training dataset and the validation_set. The
        format of this SFrame must be the same as the training set.
        By default this argument is set to 'auto' and a validation set is
        automatically sampled and used for progress printing. If
        validation_set is set to None, then no additional metrics
        are computed.


    Returns
    -------
      out : :class:`~graphlab.distributed._dml_job_status.DMLJobStatus`
          An object that tracks the execution of the distributed training job.

    See Also
    --------
    LogisticClassifier, graphlab.boosted_trees_classifier.BoostedTreesClassifier,
    graphlab.svm_classifier.SVMClassifier, graphlab.classifier.create

    Notes
    -----
    - Categorical variables are encoded by creating dummy variables. For a
      variable with :math:`K` categories, the encoding creates :math:`K-1` dummy
      variables, while the first category encountered in the data is used as the
      baseline.

    - For prediction and evaluation of logistic regression models with sparse
      dictionary inputs, new keys/columns that were not seen during training
      are silently ignored.

    - During model creation, 'None' values in the data will result in an error
      being thrown.

    - A constant term is automatically added for the model intercept. This term
      is not regularized.

    - Standard errors on coefficients are only availiable when `solver=newton`
      or when the default `auto` solver option choses the newton method and if
      the number of examples in the training data is more than the number of
      coefficients. If standard errors cannot be estimated, a column of `None`
      values are returned.


    References
    ----------
    - `Wikipedia - logistic regression
      <http://en.wikipedia.org/wiki/Logistic_regression>`_

    - Hoerl, A.E. and Kennard, R.W. (1970) `Ridge regression: Biased Estimation
      for Nonorthogonal Problems
      <http://amstat.tandfonline.com/doi/abs/10.1080/00401706.1970.10488634>`_.
      Technometrics 12(1) pp.55-67

    - Tibshirani, R. (1996) `Regression Shrinkage and Selection via the Lasso <h
      ttp://www.jstor.org/discover/10.2307/2346178?uid=3739256&uid=2&uid=4&sid=2
      1104169934983>`_. Journal of the Royal Statistical Society. Series B
      (Methodological) 58(1) pp.267-288.

    - Zhu, C., et al. (1997) `Algorithm 778: L-BFGS-B: Fortran subroutines for
      large-scale bound-constrained optimization
      <http://dl.acm.org/citation.cfm?id=279236>`_. ACM Transactions on
      Mathematical Software 23(4) pp.550-560.

    - Beck, A. and Teboulle, M. (2009) `A Fast Iterative Shrinkage-Thresholding
      Algorithm for Linear Inverse Problems
      <http://epubs.siam.org/doi/abs/10.1137/080716542>`_. SIAM Journal on
      Imaging Sciences 2(1) pp.183-202.


    Examples
    --------

    Given an :class:`~graphlab.SFrame` ``sf``, a list of feature columns
    [``feature_1`` ... ``feature_K``], and a target column ``target`` with 0 and
    1 values, create a
    :class:`~graphlab.logistic_classifier.LogisticClassifier` as follows:

    >>> hdp_env = graphlab.deploy.hadoop_cluster.create('my-first-hadoop-cluster',
    ...    'hdfs://path-to-turi-distributed-installation')
    >>> data =  graphlab.SFrame('https://static.turi.com/datasets/regression/houses.csv')
    >>> data['is_expensive'] = data['price'] > 30000
    >>> distr_job = graphlab.distributed.logistic_classifier.submit_training_job(hdp_env, data, 'is_expensive')
    >>> model = distr_job.get_results()
    """

    _mt._get_metric_tracker().track('distributed.toolkit.classifier.logistic_classifier.submit_training_job')

    # Regression model names.
    model_name = "classifier_logistic_regression"
    solver = solver.lower()

    dml_obj = _sl.create(dataset, target, model_name, env=env, features=features,
                        validation_set = validation_set,
                        l2_penalty=l2_penalty, l1_penalty = l1_penalty,
                        feature_rescaling = feature_rescaling,
                        convergence_threshold = convergence_threshold,
                        step_size = step_size,
                        solver = solver,
                        lbfgs_memory_level = lbfgs_memory_level,
                        max_iterations = max_iterations,
                        class_weights = class_weights)

    return dml_obj
