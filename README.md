# 🏗️ Armazena+ | Gestão de Estoque de Obra

O **Armazena+** é uma aplicação desktop desenvolvida para otimizar o controle e a movimentação de materiais e ferramentas em canteiros de obras. Com uma interface moderna, o sistema oferece controle de acesso baseado em funções, monitoramento visual de indicadores, alertas inteligentes de estoque baixo e um histórico completo de auditoria.

---

## 📝 Descrição do Projeto

O sistema foi projetado para atender diferentes perfis de operadores dentro de uma obra, garantindo que cada usuário acesse apenas as ferramentas necessárias para sua função.

### ✨ Principais Funcionalidades:
* **Controle de Acesso (Perfis Dinâmicos):** Diferenciação de telas e permissões para perfis como *Administrador*, *Entrada de Materiais*, *Saída de Materiais* e *Fiscalização/Devoluções*.
* **Gestão Híbrida de Itens:** Gerenciamento de itens **Consumíveis** (com controle volumétrico e unidade de medida) e **Ferramentas** (com controle de status e responsável pelo empréstimo).
* **Painel de Indicadores (Dashboard):** Gráficos gerados em tempo real que exibem o top 5 de itens com maior volume em estoque e o histórico de itens mais retirados.
* **Alertas Inteligentes de Estoque:** Sistema dinâmico que destaca visualmente em amarelo (atenção) ou vermelho (crítico) os insumos com baixo volume, calculando os limites de forma proporcional ao saldo inicial do produto.
* **Histórico de Auditoria:** Registro automatizado de todas as ações importantes (logins, logouts, cadastros, entradas, saídas e exclusões) com data, hora e usuário responsável.

---

## 🚀 Tecnologias Utilizadas

O projeto foi desenvolvido utilizando o ecossistema Python e as seguintes bibliotecas:
* **Python 3** - Linguagem base do projeto.
* **CustomTkinter** - Interface gráfica moderna e customizável (com suporte nativo a temas claros/escuros).
* **SQLite3** - Banco de dados relacional leve e local para persistência dos dados de estoque e logs.
* **Matplotlib** - Renderização de gráficos estatísticos integrados à interface.
* **Pillow (PIL)** - Processamento e renderização de imagens (como o logotipo da aplicação).
* **Python-dotenv** - Gerenciamento seguro de credenciais de usuários por meio de variáveis de ambiente.

---

## 📋 Requisitos para Execução

Antes de rodar a aplicação, certifique-se de ter instalado em sua máquina:
1.  **Python 3.8** ou superior.
2.  Gerenciador de pacotes **pip**.

Além disso, a aplicação depende de dois arquivos auxiliares no mesmo diretório do script principal:
* `logo.png`: Imagem da logo exibida na tela de login e menu lateral.
* `users.env`: Arquivo de configuração contendo as credenciais de acesso.
