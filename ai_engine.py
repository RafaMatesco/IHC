import dspy
import sqlite3

# Configuração do modelo local via Ollama
dspy.settings.configure(
    lm=dspy.LM(
        model="ollama/llama3.2", # Ou "ollama/llama3.2:latest" se mudou antes
        api_base="http://localhost:11434",
        max_tokens=500,
        temperature=0.7,
    )
)

# Etapa 1: Transforma texto em SQL (Sua lógica original)
class GenerateSQL(dspy.Signature):
    """Generate SQL from natural language. Respond ONLY with the reasoning and the valid SQL query. Do not add any conversational text or formatting.

    Database schema:
    - clientes: id, nome, email, data_cadastro
    - produtos: id, nome, categoria, preco, estoque
    - pedidos: id, cliente_id, produto_id, quantidade, status
    """
    question = dspy.InputField(desc="Natural language question")
    sql_query = dspy.OutputField(desc="Valid SQL query")

# Etapa 2: NOVA! Pega os dados brutos do banco e transforma em uma resposta humana
class AnswerQuestion(dspy.Signature):
    """Você é um assistente de e-commerce gentil. Responda à pergunta do usuário em português claro e natural, utilizando estritamente os dados retornados do banco de dados fornecidos abaixo."""
    question = dspy.InputField(desc="Pergunta feita pelo usuário")
    data_results = dspy.InputField(desc="Dados brutos retornados do banco de dados")
    answer = dspy.OutputField(desc="Resposta final em linguagem natural e amigável")


class SQLGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generator = dspy.ChainOfThought(GenerateSQL)
        self.refiner = dspy.ChainOfThought("question, sql_query, error -> refined_sql")
        # Inicializa o novo componente que vai falar de forma natural
        self.responder = dspy.ChainOfThought(AnswerQuestion)

    def forward(self, question, conn):
        # 1. Gera a query SQL
        output = self.generator(question=question)
        sql = output.sql_query.strip()
        sql = sql.replace("```sql", "").replace("```", "").strip()

        try:
            results = conn.execute(sql).fetchall()
            # 2. Se deu certo, passa o resultado para a LLM criar o texto natural
            text_response = self.responder(question=question, data_results=str(results))
            return dspy.Prediction(sql_query=sql, results=results, text_answer=text_response.answer, error=None)
            
        except Exception as e:
            # Tenta refinar caso dê erro de sintaxe SQL
            refined = self.refiner(question=question, sql_query=sql, error=str(e))
            refined_sql = refined.refined_sql.replace("```sql", "").replace("```", "").strip()
            try:
                results = conn.execute(refined_sql).fetchall()
                # Passa o resultado refinado para gerar o texto natural
                text_response = self.responder(question=question, data_results=str(results))
                return dspy.Prediction(sql_query=refined_sql, results=results, text_answer=text_response.answer, error=None)
            except Exception as e2:
                return dspy.Prediction(sql_query=refined_sql, results=None, text_answer=None, error=str(e2))

def create_examples():
    return [
        dspy.Example(
            question="Quantos produtos temos em estoque na categoria Eletrônicos?",
            reasoning="Preciso somar a coluna estoque filtrando apenas a categoria Eletrônicos.",
            sql_query="SELECT SUM(estoque) FROM produtos WHERE categoria = 'Eletrônicos'"
        ).with_inputs("question"),
        dspy.Example(
            question="Qual o nome do cliente que fez o pedido número 1?",
            reasoning="Preciso fazer um JOIN entre clientes e pedidos para achar o nome correspondente ao pedido 1.",
            sql_query="SELECT c.nome FROM clientes c JOIN pedidos p ON c.id = p.cliente_id WHERE p.id = 1"
        ).with_inputs("question"),
        dspy.Example(
            question="Qual é o produto mais barato?",
            reasoning="Devo ordenar os produtos pelo preço em ordem crescente e pegar o primeiro.",
            sql_query="SELECT nome, preco FROM produtos ORDER BY preco ASC LIMIT 1"
        ).with_inputs("question")
    ]

generator = SQLGenerator()
generator.generator.demos = create_examples()