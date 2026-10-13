import pandas as pd

# loading Dataset
df = pd.read_csv('data/processed/clean_dataset.csv')


# Defining the Quantitative Columns
cols_analizar = [
    'char_count',
    'word_count',
    'url_count',
    'urgency_score',
    'is_threat',
]


# Calculating Metrics
resumen = df[cols_analizar].agg(
    [
        'mean',
        'std',
        'median',
        lambda x: x.quantile(0.75) - x.quantile(0.25),
        'skew',
        'kurt',
    ]
)


# Renaming Rows
resumen.index = [
    'Media',
    'Desv. Est.',
    'Mediana',
    'IQR',
    'Asimetria (Skew)',
    'Curtosis',
]


# Snowflake Formatting
print('\nUnivariate Descriptive Table\n')
print(resumen.round(4).T.to_string())