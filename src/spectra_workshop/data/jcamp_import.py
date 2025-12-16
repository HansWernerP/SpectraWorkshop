import jcamp
import pandas as pd


def read_jcamp(filename: str) -> pd.DataFrame:

    # Alle Spektren einlesen
    data = jcamp.jcamp_readfile(filename)

    # Wenn mehrere Spektren vorhanden sind (Multi-Block)
    dfs = []
    if 'children' in data:
        for child in data['children']:
            df = pd.Series(child)
            #     {
            #     'Wellenlänge': child['x'],
            #     'Absorbanz': child['y']
            # })
            # df['Titel'] = child.get('title', '')
            # df['Protein'] = child.get('concentrations', {}).get('Protein i. TS', None)
            # dfs.append(df)
            print(df)
    else:
        # Einzelnes Spektrum
        df = pd.DataFrame({
            'Wellenlänge': data['x'],
            'Absorbanz': data['y']
        })
        df['Titel'] = data.get('title', '')
        df['Protein'] = data.get('concentrations', {}).get('Protein i. TS', None)
        dfs.append(df)

    # Alle DataFrames kombinieren
    combined_df = pd.concat(dfs, keys=range(len(dfs)))
