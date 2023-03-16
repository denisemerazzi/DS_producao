## Como funciona o Bot Telegram?
Foram construídos dois arquivos com extensão .py (API_Handler.py e Rossmann.py). 

A API Handler tem a tarefa de carregar o modelo em produção, receber os dados inéditos e enviar a requisição para o arquivo Rossmann.py, onde é aplicado aos novos dados o mesmo tratamento que receberam os dados de treino (limpeza, encodings, feature engineering). 

Após, esses dados vão para o modelo treinado (XGBoost), que devolve a predição via API. 

O usuário, faz a requisição da loja que deseja saber a previsão de vendas, via mensagem pelo APP Tetegram do seu celular. Essa requisição é recebida pela API Rossmann, que carrega os dados na memória, filtra a loja desejada e passa para a API Handler, que após passar os dados para o modelo, devolve as predições para o Rossmann e este devolve para o usuário via Telegram.
