from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

def get_model_name(model, kernel=None):
    if isinstance(model, SVC):
        if kernel == 'rbf':
            return "SVM: Gaussiano"
        else:
            return "SVM: Linear"
    elif isinstance(model, DecisionTreeClassifier):
        return "Árvore de Decisão"
    elif isinstance(model, RandomForestClassifier):
        return "Floresta Aleatória"
    elif isinstance(model, LogisticRegression):
        return "Regressão Logística"
    else:
        return model.__class__.__name__
