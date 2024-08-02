from datetime import date, timedelta
import streamlit as st
import pandas as pd

# Parâmetros (com Streamlit input)
st.title("Alocação de Alunos")

uploaded_file = st.file_uploader("Escolha um arquivo CSV com Nome e Matrícula", type="csv")

if uploaded_file is not None:
    df_alunos = pd.read_csv(uploaded_file)
    alunos = df_alunos["Nome"].tolist()
    num_alunos = len(alunos)

    professores_input = st.text_area(
        "Professores e suas capacidades (Nome:Quantidade, separados por vírgula):",
        value="A:10, B:10, C:10, D:10"
    )

    professores = {}
    capacidades = []
    disponibilidade_professores = {}

    dias_da_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

    dias_indices = {
        "Segunda-feira": 0,
        "Terça-feira": 1,
        "Quarta-feira": 2,
        "Quinta-feira": 3,
        "Sexta-feira": 4,
        "Sábado": 5,
        "Domingo": 6
    }

    for prof_data in professores_input.split(","):
        nome, capacidade = prof_data.strip().split(":")
        professores[nome] = int(capacidade)
        capacidades.append(int(capacidade))
        # Usando multiselect para selecionar os dias de disponibilidade
        dias_disponiveis = st.multiselect(f"Selecione os dias disponíveis para {nome}:", dias_da_semana, default=["Terça-feira"])
        dias_disponiveis_indices = [dias_indices[dia] for dia in dias_disponiveis]
        disponibilidade_professores[nome] = dias_disponiveis_indices

    capacidade_total = sum(professores.values())
    if capacidade_total != num_alunos:
        st.error(f"A capacidade total dos professores ({capacidade_total}) não corresponde ao número de alunos ({num_alunos}).")
        st.stop()

    data_inicio = st.date_input("Data de Início:", value=date(2024, 8, 2))
    data_fim = st.date_input("Data de Fim:", value=date(2024, 12, 10))

    # Dicionário para armazenar a alocação
    alocacao = {}

    # Função para gerar um ciclo completo de alocações para um dia
    def gerar_ciclo_diario(alunos, professores, offset, dia_semana):
        alocacao_dia = {}
        alunos_rotacionados = alunos[offset:] + alunos[:offset]
        alunos_restantes = alunos_rotacionados[:]
        for professor, capacidade in professores.items():
            if dia_semana in disponibilidade_professores[professor]:
                alocacao_dia[professor] = alunos_restantes[:capacidade]
                alunos_restantes = alunos_restantes[capacidade:]
        return alocacao_dia

    # Loop principal para cada dia no intervalo
    data_atual = data_inicio
    offset = 0  # Offset inicial para rotação
    indice_capacidade = 0  # Índice para acessar a capacidade do professor atual
    while data_atual <= data_fim:
        dia_semana = data_atual.weekday()
        alocacao_dia = gerar_ciclo_diario(alunos, professores, offset, dia_semana)
        if alocacao_dia:  # Só faz a rotação se houve alocação
            alocacao[data_atual] = alocacao_dia
            # Calcula o novo offset com a soma das capacidades dos professores que tiveram alocações
            offset = (offset + capacidades[indice_capacidade]) % len(alunos)
            indice_capacidade = (indice_capacidade + 1) % len(capacidades)
        data_atual += timedelta(days=1)

    # Impressão da alocação com Streamlit em tabelas
    st.header("Alocação de Alunos:")
    for data, profs_alunos in alocacao.items():
        if profs_alunos:  # Somente mostra se houver alocação para o dia
            st.markdown(f"**Encontros para {data.strftime('%d/%m/%Y')} ({data.strftime('%A')}):**")
            df = pd.DataFrame.from_dict(profs_alunos, orient='index').transpose()
            st.dataframe(df)

else:
    st.warning("Por favor, faça o upload de um arquivo CSV.")
