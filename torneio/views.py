from django.shortcuts import render
from .models import Time, Jogador, Partida

def index(request):
    """
    View principal que alimenta o Dashboard da Copa Área 7.
    Ordenação: Vitórias > Saldo de Gols > Gols Pró.
    """
    # Buscamos todos os times. 
    # A ordenação segue a lógica: Mais vitórias primeiro, 
    # depois melhor saldo de gols (indireto via gols_pro) e menos derrotas.
    times = Time.objects.all().order_by('-vitorias', '-gols_pro', 'derrotas')
    
    # Se você quiser uma ordenação ainda mais precisa, 
    # podemos converter para lista e ordenar pelos 'pontos' (property)
    times = sorted(times, key=lambda t: (t.pontos, t.vitorias, t.saldo_gols), reverse=True)

    # Pega os 5 jogadores com mais gols para o bloco de Artilharia
    artilheiros = Jogador.objects.all().order_by('-gols')[:5]
    
    # Opcional: Pegar as últimas 5 partidas realizadas
    ultimas_partidas = Partida.objects.all().order_by('-data_partida')[:5]
    
    return render(request, 'torneio/index.html', {
        'times': times,
        'artilheiros': artilheiros,
        'ultimas_partidas': ultimas_partidas
    })

def tabela_classificacao(request):
    """
    View secundária exclusiva para a tabela detalhada.
    """
    times = Time.objects.all()
    # Ordenação por Pontos (via Python sorted devido à @property)
    times = sorted(times, key=lambda t: (t.pontos, t.vitorias, t.saldo_gols), reverse=True)
    
    return render(request, 'torneio/tabela.html', {'times': times})