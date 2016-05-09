import imp, operator, os
import numpy as np
from collections import defaultdict
import ujson as json
import timeit, math

from sklearn import cross_validation, svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.learning_curve import learning_curve, validation_curve
from sklearn.metrics import classification_report, precision_recall_curve
from sklearn.preprocessing import label_binarize
from sklearn.externals import joblib

from preprocess import *

def read_words(file_name):
    """
    Returns a list of lines read from the given file.
    """
    with open(file_name, 'r') as f:
        return f.readlines()

def load_dataset(words_work_file_name, norm_tweets_file_name):
    """
    Creates training examples X with labels y suitable for use with sklearn classifiers from preprocessed data.
    It uses CountVectorizer to create features from dictionary of words contained in words_work_file_name and
    all unigrams, bigrams and trigrams extracted from normalized tweets contained in norm_tweets_file_name.
    
    Input:
        words_work_file_name - (Dictionary) file containing normalized words from the whole dataset, one word per line
        norm_tweets_file_name - file containing labeled normalized tweets
    
    Output:
        X - matrix of training examples
        y - vector of labels
        vectorizer - sklearn CountVectorizer used for ngram tokenization
    """
    words = read_words(words_work_file_name)
    labeled_tweets = read_normalized_tweets(norm_tweets_file_name) # list of tuples (label, string_of_normalized_words)
    
    vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 3), max_df=0.75, max_features=10000)
    vectorizer.fit(words)
    
    m = len(labeled_tweets)
    tweet_list = []
    Y = np.empty((m,))

    for idx, t in enumerate(labeled_tweets):
        Y[idx, ] = t[0]
        tweet_list.append(t[1])

    X = vectorizer.transform(tweet_list)

    return X, Y, vectorizer

def print_most_significant_features(coefficients, vectorizer, N):
    """
    nunmp.nonzero ---- yields the indices of the array 
    where the condition is true.
    """
    coefficients = coefficients.toarray()

    nonzero_indices_pos = np.nonzero(coefficients > 0)
    nonzero_indices_neg = np.nonzero(coefficients <= 0)
    feature_names = vectorizer.get_feature_names()

    print 'top %d Positive features' % N 
    p = dict((i, coefficients[0, i]) for i in nonzero_indices_pos[1])
    p_sorted = sorted(p.items(), key=operator.itemgetter(1), reverse=True)
    for t in p_sorted[:N]:
        print '%s (%s)' % (feature_names[t[0]], t[1])
        
    print

    print 'top %d Negative features' % N
    n = dict((i, coefficients[0, i]) for i in nonzero_indices_neg[1])
    n_sorted = sorted(n.items(), key=operator.itemgetter(1))
    for t in n_sorted[:N]:
        print '%s (%s)' % (feature_names[t[0]], t[1])
        
def plot_learning_curves(clf, scoring, X, y):
    try:
        imp.find_module('matplotlib')
    except ImportError:
        "matplotlib module not found, can't plot learning curves"
        return
    
    import matplotlib.pyplot as plt

    train_sizes, train_scores, test_scores = learning_curve(clf, X, y, train_sizes=np.linspace(0.05, 1.0, 10), scoring=scoring, cv=10)
    
    train_scores_mean = np.mean(train_scores, axis=1)
    train_scores_std = np.std(train_scores, axis=1)

    test_scores_mean = np.mean(test_scores, axis=1)
    test_scores_std = np.std(test_scores, axis=1)
    
    plt.title('Learning curves for SVM optimized using a score function ' + scoring)
    plt.xlabel('# of training examples')
    plt.ylabel('score')
    plt.grid()

    plt.fill_between(train_sizes, train_scores_mean - train_scores_std, train_scores_mean + train_scores_std, alpha=0.1, color="r")
    plt.fill_between(train_sizes, test_scores_mean - test_scores_std, test_scores_mean + test_scores_std, alpha=0.1, color="g")

    plt.plot(train_sizes, train_scores_mean, 'o-', color="r", label="Training score")
    plt.plot(train_sizes, test_scores_mean, 'o-', color="g", label="Cross-validation score")

    plt.legend(loc="best")
    
    plt.savefig('learning_curve_' + scoring + '.png')
    # plt.show()
        
def check_preprocessed_data():
    """
    Checks if files created during preprocessing step exist. 
    Raises an exception if they don't.
    """
    required_files = [norm_tweets_file_name, words_work_file_name]
    for required_file in required_files:
        if not os.path.isfile(required_file):
            raise Exception('%s does not exist, please run preprocess.py first.' % (required_file))
            
def train_classifier(X_train, y_train, scoring):
    """
    Trains an SVM classifier using the training data and a grid-search to fit the estimator hyperparameters.
    """
    # optimized hyperparameters
    weight_dicts = [{1:1, -1:1}, {1:5, -1:1}, {1:1, -1:5}, {1:10, -1:1}, {1:1, -1:10}, {1:20, -1:1}, {1:1, -1:20}, {1:30, -1:1}, {1:1, -1:30}, {1:50, -1:1}, {1:1, -1:50}]

    param_grid = [
    {'C':[0.01, 0.1, 1, 10, 100, 1000], 'kernel':['linear'], 'class_weight':weight_dicts, 'probability':[True, False], 'shrinking':[True, False]}
    ]

    print 'Performing grid search to find an optimal estimator using scoring function %s and a parameter grid %s' % (scoring, param_grid)    
    clf = GridSearchCV(svm.SVC(C=1,), param_grid, cv=10, scoring=scoring)
    print

    clf.fit(X_train, y_train)
    print 'Grid search complete.'

    print_grid_search_results(clf, scoring)
    print
    
    return clf

def print_grid_search_results(clf, scoring):
    print 'Grid scores based on score function %s:' % (scoring)
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r"
              % (mean_score, scores.std() / 2, params))

    print
    print 'parameter setting that gave the best results on the hold out data:'
    print clf.best_params_

    print
    print 'score of best_estimator on the left out data:'
    print clf.best_score_

    print
    print 'estimator that was chosen by the grid search:'
    print clf.best_estimator_

def print_cv_classification_report(clf, X_test, y_test):
    """
    Prints weighted average of precision, recall and F1-score over each of the classes in the test dataset.
    
    see sklearn.metrics.classification_report
    """
    print 'Classification report on training data (with cross validation):'
    y_true, y_pred = y_test, clf.predict(X_test)

    target_names = ['others', 'suicidal']
    print classification_report(y_true, y_pred, target_names=target_names)

def analyze_classifier(clf, X, y, X_test, y_test, vectorizer):
    """
    Analyzes the classifier.
    Input:
        clf - GridSearchCV instance
        X_test - test examples
        y_test - test labels
    """
    print_cv_classification_report(clf, X_test, y_test)
    print
    
    best_estimator = clf.best_estimator_

    print_most_significant_features(best_estimator.coef_, vectorizer, 20)
    print
    
    plot_learning_curves(best_estimator, clf.scoring, X, y)

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    check_preprocessed_data()
    
    X, y, vectorizer = load_dataset(words_work_file_name, norm_tweets_file_name)
    # joblib.dump(vectorizer, 'amt_1+2_pro_vectorizer_20160401.pkl')

    # split the data into train/test sets making test set one tenth of all data
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.1, random_state=5)

    # scoring = 'roc_auc', 'precision', 'f1', 'recall', 'accuracy'
    scoring = 'accuracy'

    clf = train_classifier(X_train, y_train, scoring)
    # joblib.dump(clf, 'amt_1+2_pro_' + scoring + '_SVC_20160401.pkl')

    analyze_classifier(clf, X, y, X_test, y_test, vectorizer)

    print 'Done.'

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()