# -*- coding: utf-8 -*-
"""Final_work.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nmYivVzHFYP2s_nO-b0hMzz3n3YpFEBd

# Шаг 1. Загрузка необходимых библиотек
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn import metrics
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV
from statsmodels.stats.diagnostic import normal_ad
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson
from scipy import stats
from scipy.special import inv_boxcox

"""# Шаг 2. Загрузка необходимого датасета по стоимостям машин из Kaggle"""

#!mkdir -p ~/.kaggle/ # создать .kaggle папку на диске

#!gdown --id 1ITV6ymlFBy5wTOxgTmRH4HrocTw1C7jC # загрузка файла с моего диска. Тут вход на тестовый аккаунт преподавателя. Вам нужен ваш аккаунт

# https://drive.google.com/file/d/1ITV6ymlFBy5wTOxgTmRH4HrocTw1C7jC/view?usp=sharing

#!cp /content/kaggle.json ~/.kaggle

#!chmod 600 /root/.kaggle/kaggle.json

#!kaggle datasets download -d nehalbirla/vehicle-dataset-from-cardekho #датасет прогноза погоды

#https://www.kaggle.com/datasets/zalando-research/fashionmnist

#!unzip vehicle-dataset-from-cardekho.zip

"""# Шаг 3. Чтение Датасета"""

df = pd.read_csv('car data.csv')

"""# Шаг 4. Визуализация датасета"""

df.head(5)

"""В данном случае целевой прогнозируемой переменной будет являться "Selling Price"
"""

df.shape

"""Датасет состоит из 301 строки и 9 столбцов

Основная информация по датасету
"""

df.info()

"""Нет пустых значений

Обзор колонок с численными значениями
"""

df.describe(include='number')

"""Обзор колонок с нечисленными значениями"""

df.describe(include='object')

"""# Шаг 5. Подготовка данных"""

df['Car_Name'].nunique()

"""98 уникальных значений машин. Рекомендуется убрать эти данные из датасета"""

df.drop('Car_Name', axis=1, inplace=True)

"""Вместо года проведем разбалловку где минимальное значение 1 примет 2003 год, а максимальный 2018 максмимальный балл"""

df.insert(0, "Age", df["Year"].max()+1-df["Year"] )
df.drop('Year', axis=1, inplace=True)
df.head()

"""Рассмотрим данные на выбросы"""

sns.set_style('darkgrid')
colors = ['#0055ff', '#ff7000', '#23bf00']
CustomPalette = sns.set_palette(sns.color_palette(colors))

OrderedCols = np.concatenate([df.select_dtypes(exclude='object').columns.values,
                              df.select_dtypes(include='object').columns.values])

fig, ax = plt.subplots(2, 4, figsize=(15,7),dpi=100)

for i,col in enumerate(OrderedCols):
    x = i//4
    y = i%4
    if i<5:
        sns.boxplot(data=df, y=col, ax=ax[x,y])
        ax[x,y].yaxis.label.set_size(15)
    else:
        sns.boxplot(data=df, x=col, y='Selling_Price', ax=ax[x,y])
        ax[x,y].xaxis.label.set_size(15)
        ax[x,y].yaxis.label.set_size(15)

plt.tight_layout()
plt.show()

outliers_indexes = []
target = 'Selling_Price'

for col in df.select_dtypes(include='object').columns:
    for cat in df[col].unique():
        df1 = df[df[col] == cat]
        q1 = df1[target].quantile(0.25)
        q3 = df1[target].quantile(0.75)
        iqr = q3-q1
        maximum = q3 + (1.5 * iqr)
        minimum = q1 - (1.5 * iqr)
        outlier_samples = df1[(df1[target] < minimum) | (df1[target] > maximum)]
        outliers_indexes.extend(outlier_samples.index.tolist())


for col in df.select_dtypes(exclude='object').columns:
    q1 = df[col].quantile(0.25)
    q3 = df[col].quantile(0.75)
    iqr = q3-q1
    maximum = q3 + (1.5 * iqr)
    minimum = q1 - (1.5 * iqr)
    outlier_samples = df[(df[col] < minimum) | (df[col] > maximum)]
    outliers_indexes.extend(outlier_samples.index.tolist())

outliers_indexes = list(set(outliers_indexes))
print('{} outliers were identified, whose indices are:\n\n{}'.format(len(outliers_indexes), outliers_indexes))

"""Недопустимо отбрасывать наблюдение только потому, что оно является выбросом. Они могут быть законными наблюдениями, и важно изучить природу выброса, прежде чем принимать решение о том, удалять его или нет. Удалять выбросы разрешается в двух случаях:

Выброс обусловлен неверно введенными или измеренными данными

Выброс создает значимую ассоциацию
"""

# Outliers Labeling
df1 = df.copy()
df1['label'] = 'Normal'
df1.loc[outliers_indexes,'label'] = 'Outlier'

# Removing Outliers
removing_indexes = []
removing_indexes.extend(df1[df1[target]>33].index)
removing_indexes.extend(df1[df1['Kms_Driven']>400000].index)
df1.loc[removing_indexes,'label'] = 'Removing'

# Plot
target = 'Selling_Price'
features = df.columns.drop(target)
colors = ['#0055ff','#ff7000','#23bf00']
CustomPalette = sns.set_palette(sns.color_palette(colors))
fig, ax = plt.subplots(nrows=3 ,ncols=3, figsize=(15,12), dpi=200)

for i in range(len(features)):
    x=i//3
    y=i%3
    sns.scatterplot(data=df1, x=features[i], y=target, hue='label', ax=ax[x,y])
    ax[x,y].set_title('{} vs. {}'.format(target, features[i]), size = 15)
    ax[x,y].set_xlabel(features[i], size = 12)
    ax[x,y].set_ylabel(target, size = 12)
    ax[x,y].grid()

ax[2, 1].axis('off')
ax[2, 2].axis('off')
plt.tight_layout()
plt.show()

"""Удаляемые выбросы будут связаны со следующими показателями:"""

removing_indexes = list(set(removing_indexes))
removing_indexes

"""Эти две выборки сильно отличаются от общей картины, наблюдаемой на диаграммах рассеяния данных. Поскольку линейная регрессия чувствительна к выбросам, мы отбросим их.

Поиск пропущенных значений
"""

df.isnull().sum()

"""Поиск дублей"""

df[df.duplicated(keep=False)]

"""Поскольку возможны автомобили с одинаковыми характеристиками, мы не отбрасываем дубликаты.

Удаляем лишнее
"""

df1 = df.copy()
df1.drop(removing_indexes, inplace=True)
df1.reset_index(drop=True, inplace=True)

"""# Шаг 6. Разведочный анализ данных

Анализ категориальных переменных
"""

CatCols = ['Fuel_Type', 'Seller_Type', 'Transmission']

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(15,5), dpi=100)
colors = ['#0055ff', '#ff7000', '#23bf00']
CustomPalette = sns.set_palette(sns.color_palette(colors))

for i in range(len(CatCols)):
    graph = sns.countplot(x=CatCols[i], data=df1, ax=ax[i])
    ax[i].set_xlabel(CatCols[i], fontsize=15)
    ax[i].set_ylabel('Count', fontsize=12)
    ax[i].set_ylim([0,300])
    ax[i].set_xticklabels(ax[i].get_xticklabels(), fontsize=12)
    for cont in graph.containers:
        graph.bar_label(cont)

plt.suptitle('Frequency Distribution of Categorical Variables', fontsize=20)
plt.tight_layout()
plt.show()

"""Вывод:
Существует 3 категории Fuel_Type. Наибольшую частоту встречаемости имеет бензин, наименьшую - КПГ.
Существует 2 категории типа продавца. Наибольшая частота встречается у дилера, наименьшая - у частного лица.
Существует 2 категории трансмиссии. Наибольшая частота встречается у механической коробки передач, наименьшая - у автоматической.

Анализ численных переменных
"""

NumCols = ['Age', 'Selling_Price', 'Present_Price', 'Kms_Driven', 'Owner']

fig, ax = plt.subplots(nrows=2, ncols=3, figsize=(15,10), dpi=200)
c = '#0055ff'

for i in range(len(NumCols)):
    row = i//3
    col = i%3
    values, bin_edges = np.histogram(df1[NumCols[i]],
                                     range=(np.floor(df1[NumCols[i]].min()), np.ceil(df1[NumCols[i]].max())))
    graph = sns.histplot(data=df1, x=NumCols[i], bins=bin_edges, kde=True, ax=ax[row,col],
                         edgecolor='none', color=c, alpha=0.4, line_kws={'lw': 2.5})
    ax[row,col].set_xlabel(NumCols[i], fontsize=15)
    ax[row,col].set_ylabel('Count', fontsize=12)
    ax[row,col].set_xticks(np.round(bin_edges,1))
    ax[row,col].set_xticklabels(ax[row,col].get_xticks(), rotation = 45)
    ax[row,col].grid(color='lightgrey')
    for j,p in enumerate(graph.patches):
        ax[row,col].annotate('{}'.format(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()+1),
                             ha='center', fontsize=10 ,fontweight="bold")

    textstr = '\n'.join((
    r'$\mu=%.2f$' %df1[NumCols[i]].mean(),
    r'$\sigma=%.2f$' %df1[NumCols[i]].std(),
    r'$\mathrm{median}=%.2f$' %np.median(df1[NumCols[i]]),
    r'$\mathrm{min}=%.2f$' %df1[NumCols[i]].min(),
    r'$\mathrm{max}=%.2f$' %df1[NumCols[i]].max()
    ))
    ax[row,col].text(0.6, 0.9, textstr, transform=ax[row,col].transAxes, fontsize=10, verticalalignment='top',
                     bbox=dict(boxstyle='round',facecolor='#509aff', edgecolor='black', pad=0.5))

ax[1, 2].axis('off')
plt.suptitle('Distribution of Numerical Variables', fontsize=20)
plt.tight_layout()
plt.show()

"""# Шаг 7. Кодирование категориальных переменных"""

CatCols = ['Fuel_Type', 'Seller_Type', 'Transmission']

df1 = pd.get_dummies(df1, columns=CatCols, drop_first=True)
df1.head(5)

"""# Шаг 8. Анализ корреляций"""

target = 'Selling_Price'
cmap = sns.diverging_palette(125, 28, s=100, l=65, sep=50, as_cmap=True)
fig, ax = plt.subplots(figsize=(9, 8), dpi=80)
ax = sns.heatmap(pd.concat([df1.drop(target,axis=1), df1[target]],axis=1).corr(), annot=True, cmap=cmap)
plt.show()

"""Целевая переменная "Цена продажи" сильно коррелирует с Present_Price, Seller_Type и Fuel_Type.
Некоторые независимые переменные, такие как Fuel_Type_Petrol и Fuel_Type_Disel, сильно коррелируют между собой, что называется мультиколлинеарностью.

# Шаг 9. Построение модели Линейной Регрессии
"""

X = df1.drop('Selling_Price', axis=1)
y = df1['Selling_Price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=21)

print('X_train shape: ', X_train.shape)
print('X_test shape: ', X_test.shape)
print('y_train shape: ', y_train.shape)
print('y_test shape: ',y_test.shape)

print(X_train)
print(y_train)
X_train.to_excel (r'mydata_X.xlsx')
X_train.to_excel (r'mydata_X.xlsx')

y_test_actual = y_test

"""Маштабирование данных с помощью StandartScaler"""

scaler = StandardScaler()
scaler.fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

"""Очень важно, что преобразования StandardScaler должны обучаться только на обучающем множестве, иначе это приведет к утечке данных.

Обучение модели
"""

linear_reg = LinearRegression()
linear_reg.fit(X_train_scaled, y_train)

"""Оценка модели"""

def model_evaluation(model, X_test, y_test, model_name):
    y_pred = model.predict(X_test)

    MAE = metrics.mean_absolute_error(y_test, y_pred)
    MSE = metrics.mean_squared_error(y_test, y_pred)
    RMSE = np.sqrt(MSE)
    R2_Score = metrics.r2_score(y_test, y_pred)
    # Plotting Graphs
    # Residual Plot of train data
    fig, ax = plt.subplots()


    # Y_test vs Y_train scatter plot
    ax.set_title('y_test vs y_pred_test')
    ax.scatter(x = y_test, y = y_pred)
    ax.set_xlabel('y_test')
    ax.set_ylabel('y_pred_test')

    plt.show()

    return pd.DataFrame([MAE, MSE, RMSE, R2_Score], index=['MAE', 'MSE', 'RMSE' ,'R2-Score'], columns=[model_name])

model_evaluation(linear_reg, X_test_scaled, y_test, 'Linear Reg.')

"""Оценка модели с помощью кросс-валидации

Использование перекрестной валидации позволяет нам с большей уверенностью оценивать метрики оценки модели, чем прежнее простое разделение "обучение-тестирование":
"""

linear_reg_cv = LinearRegression()
scaler = StandardScaler()
pipeline = make_pipeline(StandardScaler(),  LinearRegression())

kf = KFold(n_splits=6, shuffle=True, random_state=0)
scoring = ['neg_mean_absolute_error', 'neg_mean_squared_error', 'neg_root_mean_squared_error', 'r2']
result = cross_validate(pipeline, X, y, cv=kf, return_train_score=True, scoring=scoring)

MAE_mean = (-result['test_neg_mean_absolute_error']).mean()
MAE_std = (-result['test_neg_mean_absolute_error']).std()
MSE_mean = (-result['test_neg_mean_squared_error']).mean()
MSE_std = (-result['test_neg_mean_squared_error']).std()
RMSE_mean = (-result['test_neg_root_mean_squared_error']).mean()
RMSE_std = (-result['test_neg_root_mean_squared_error']).std()
R2_Score_mean = result['test_r2'].mean()
R2_Score_std = result['test_r2'].std()

pd.DataFrame({'Mean': [MAE_mean,MSE_mean,RMSE_mean,R2_Score_mean], 'Std': [MAE_std,MSE_std,RMSE_std,R2_Score_std]},
             index=['MAE', 'MSE', 'RMSE' ,'R2-Score'])

"""Модель линейной регрессии получила R2-score %85,57 при использовании 6-кратной кросс-валидации.

Конвейер - отличный способ предотвратить утечку данных, поскольку он гарантирует, что соответствующий метод будет выполняться на правильном подмножестве данных. Он идеально подходит для использования в кросс-валидации, поскольку гарантирует, что при выполнении подгонки используются только обучающие складки, а тестовое (валидационное) множество используется только для вычисления оценки точности на каждой итерации кросс-валидации
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV

rf = RandomForestRegressor()

# Number of trees in Random forest
n_estimators=list(range(500,1000,100))
# Maximum number of levels in a tree
max_depth=list(range(4,9,4))
# Minimum number of samples required to split an internal node
min_samples_split=list(range(4,9,2))
# Minimum number of samples required to be at a leaf node.
min_samples_leaf=[1,2,5,7]
# Number of fearures to be considered at each split
max_features=['auto','sqrt']

# Hyperparameters dict
param_grid = {"n_estimators":n_estimators,
              "max_depth":max_depth,
              "min_samples_split":min_samples_split,
              "min_samples_leaf":min_samples_leaf,
              "max_features":max_features}

rf_rs = RandomizedSearchCV(estimator = rf, param_distributions = param_grid)

rf_rs.fit(X_train_scaled, y_train)

model_evaluation(rf_rs, X_test_scaled, y_test, 'Random Forest')

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import RandomizedSearchCV

gb = GradientBoostingRegressor()

# Rate at which correcting is being made
learning_rate = [0.001, 0.01, 0.1, 0.2]
# Number of trees in Gradient boosting
n_estimators=list(range(500,1000,100))
# Maximum number of levels in a tree
max_depth=list(range(4,9,4))
# Minimum number of samples required to split an internal node
min_samples_split=list(range(4,9,2))
# Minimum number of samples required to be at a leaf node.
min_samples_leaf=[1,2,5,7]
# Number of fearures to be considered at each split
max_features=['auto','sqrt']

# Hyperparameters dict
param_grid = {"learning_rate":learning_rate,
              "n_estimators":n_estimators,
              "max_depth":max_depth,
              "min_samples_split":min_samples_split,
              "min_samples_leaf":min_samples_leaf,
              "max_features":max_features}

gb_rs = RandomizedSearchCV(estimator = gb, param_distributions = param_grid)

gb_rs.fit(X_train_scaled, y_train)

model_evaluation(gb_rs, X_test_scaled, y_test, 'Random Forest')

import csv
print(X_train_scaled)
with open('product_sales.csv', 'w', newline='') as file:
    # Шаг 4: используем метод csv.writer, чтобы сохранить список в файл формата CSV
    writer = csv.writer(file)
    writer.writerows(X_train_scaled) # Use writerows for nested list

y_test_pred = linear_reg.predict(X_test_scaled)
df_comp = pd.DataFrame({'Actual':y_test_actual, 'Predicted':y_test_pred})
y_test_pred_2 = rf_rs.predict(X_test_scaled)
y_test_pred_3 = gb_rs.predict(X_test_scaled)
df_comp_2 = pd.DataFrame({'Actual':y_test_actual, 'Predicted':y_test_pred_2})
df_comp_3 = pd.DataFrame({'Actual':y_test_actual, 'Predicted':y_test_pred_3})

def compare_plot(df_comp):
    df_comp.reset_index(inplace=True)
    df_comp.plot(y=['Actual','Predicted'], kind='bar', figsize=(20,7), width=0.8)
    plt.title('Predicted vs. Actual Target Values for Test Data', fontsize=20)
    plt.ylabel('Selling_Price', fontsize=15)
    plt.show()

compare_plot(df_comp)

compare_plot(df_comp_2)

compare_plot(df_comp_3)

df_exp = pd.read_excel('Experiment.xlsx', index_col=0)
df_exp

X_X_X = df_exp
print(X_X_X)

scaler = StandardScaler()
scaler.fit(X_X_X)
X_X_X_scaled = scaler.transform(X_X_X)
X_X_X_scaled

gb_rs.predict([[-7.698591886140423446e-01 , 8.804478250904161918e-01 , -8.275464082857444392e-01 , -1.628575860076396931e-01 , -4.940117600296768385e-01 , 5.089559357923956195e-01 , -7.249465119962125170e-01 , 3.769303685460225761e-01]])

def linear_regression_prediction(Age , Present_Price , Kms_Driven , Owner , Fuel_Type_Diesel ,Fuel_Type_Petrol , Seller_Type_Individual , Transmission_Manual):
  a = gb_rs.predict([[Age , Present_Price , Kms_Driven , Owner , Fuel_Type_Diesel ,Fuel_Type_Petrol , Seller_Type_Individual , Transmission_Manual]])
  return a[0]

linear_regression_prediction(-7.698591886140423446e-01 , 8.804478250904161918e-01 , -8.275464082857444392e-01 , -1.628575860076396931e-01 , -4.940117600296768385e-01 , 5.089559357923956195e-01 , -7.249465119962125170e-01 , 3.769303685460225761e-01)