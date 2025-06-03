import pandas as pd
import streamlit as st

def converter_para_dataframe(uploaded_file):
    if uploaded_file is not None:
        try:
            # Tenta como Excel primeiro
            return pd.read_excel(uploaded_file, engine="openpyxl")
        except Exception:
            pass

        # Tenta com várias codificações
        for encoding in ['utf-8', 'latin1', 'ISO-8859-1']:
            try:
                uploaded_file.seek(0)
                # Detecta automaticamente o separador
                return pd.read_csv(uploaded_file, encoding=encoding, sep=None, engine='python')
            except Exception:
                continue

        st.error("❌ Não foi possível ler o arquivo. Verifique o formato (CSV ou Excel) e a codificação (UTF-8, Latin1...).")
        return None
    return None

def aplicar_operacao(serie, operacao):
    if operacao == "Somar":
        serie = pd.to_numeric(serie, errors='coerce')
        return serie.sum()
    
    elif operacao == "Subtrair":
        serie = pd.to_numeric(serie, errors='coerce')
        return serie.iloc[0] - serie.iloc[-1] if len(serie) > 1 else serie.iloc[0]
    
    elif operacao == "Multiplicar":
        serie = pd.to_numeric(serie, errors='coerce')
        return serie.prod()
    
    elif operacao == "Dividir":
        serie = pd.to_numeric(serie, errors='coerce')
        try:
            return serie.iloc[0] / serie.iloc[1]
        except (IndexError, ZeroDivisionError):
            return None
    
    elif operacao == "Porcentagem":
        serie = pd.to_numeric(serie, errors='coerce')
        try:
            return (serie.iloc[0] / serie.iloc[1]) * 100
        except (IndexError, ZeroDivisionError, TypeError):
            return None

    elif operacao == "Contar":
        return serie.count()
    
    elif operacao == "Contagem Distinta":
        return serie.nunique()
    
    elif operacao == "Primeiro":
        return str(serie.iloc[0]) if len(serie) > 0 else None
    
    elif operacao == "Média":
        serie = pd.to_numeric(serie, errors='coerce')
        return serie.mean()
    
    else:
        return None

    




