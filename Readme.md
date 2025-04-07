# 📊 Previsão de Cancelamento de Assinatura (Churn Prediction)

**Projeto desenvolvido para a Fábrica de Projetos Ágeis**  
*Alinhado às necessidades da Avivatec e disciplinas do curso*

---

## 🎯 Objetivo
Desenvolver um **algoritmo de IA** para categorizar clientes com base na probabilidade de cancelamento de assinaturas, permitindo que empresas criem ações personalizadas de retenção.

## 🔍 Problema
Dificuldade das empresas em reter clientes em modelos de negócio baseados em assinatura (*churn rate* elevado).

## ✨ Solução
- **Classificação automática** de clientes (alto/médio/baixo risco de cancelamento).  
- **Dashboard interativo** para visualização dos resultados.  
- **Integração com APIs** de CRM para ações proativas.  

---

## 🛠️ Tecnologias
| Área          | Ferramentas                 |
|---------------|-----------------------------|
| **Back-end**  | Python(Flask), Scikit-learn |
| **Front-end** | HTML/CSS, Bootstrap         |
| **Dados**     | Pandas, Numpy, R (análise)  |
| **DevOps**    | Git, GitHub                 |


## 📅 Cronograma (Gantt)

```mermaid
gantt
    title Cronograma do Projeto
    dateFormat  YYYY-MM-DD
    axisFormat %d/%m

    section Sprint 1 (Base)
    Aprender Flask/API             :done, 2025-03-24, 6d
    Aprender HTML/CSS              :active, 2025-03-25, 17d
    Aprender Scikit-learn          :active, 2025-03-25, 17d
    Pesquisa de datasets           :active, 2025-03-25, 17d
    Análise de dados               :active, 2025-03-25, 17d
    Entrega Sprint 1               :milestone, 2025-04-11, 1d

    section Sprint 2 (Desenvolvimento)
    Projeto genérico (API)         :2025-04-11, 17d
    Importação de .csv             :2025-04-23, 5d
    Template front-end             :2025-04-11, 17d
    Relatório de dataset           :2025-04-11, 17d
    Teste de algoritmos            :2025-04-11, 17d
    Entrega Sprint 2               :milestone, 2025-04-28, 1d

    section Sprint 3 (Prototipação)
    Exportar predições (Flask)     :2025-04-29, 8d
    Testes do modelo ML            :2025-04-29, 9d
    Atributos críticos             :2025-05-08, 3d
    Compatibilidade                :2025-05-11, 7d
    Interface do usuário           :2025-04-29, 19d
    Entrega Sprint 3               :milestone, 2025-05-18, 1d

    section Sprint 4 (MVP)
    Datasets adicionais            :2025-05-19, 5d
    Modelo final de ML             :2025-05-19, 5d
    Formatar .pkl                  :2025-05-24, 2d
    Integração API                 :2025-05-26, 8d
    Preparação apresentação        :2025-05-26, 11d
    Apresentação Final (MVP)       :milestone, 2025-06-06, 1d
```

---


## 🚀 Próximos Passos
1. Finalizar pesquisa de datasets (Sprint 1).  
2. Desenvolver MVP com Flask + modelo preditivo (Sprint 2-3).  
3. Validar resultados com a Avivatec.  

---

## 📂 Estrutura do Repositório
```
/projeto-churn-prediction
├── /docs               # Documentação do projeto
├── /data               # Datasets e relatórios
├── /src                # Código-fonte
│   ├── /flask          # Back-end (Flask)
│   │    ├── /templates         
│   │    ├── /static    # CSS, Javascript
├── README.md           # Este arquivo
└── requirements.txt    # Dependências do Python
```

---


**Licença**: MIT  
**Contato**: [kobordias@email.com](#)
