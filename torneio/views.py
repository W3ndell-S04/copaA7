from django.shortcuts import render
from django.utils import timezone
from .models import Time, Jogador, Partida, ConfiguracaoGeral, FotoGaleria

def index(request):
    """
    View principal (Dashboard). 
    Focada em: Live, Top 5 Artilheiros e Integração Instagram (Galeria).
    """
    # 1. Tabela Simplificada (Top 6 para o Dashboard)
    times = Time.objects.all()
    times = sorted(times, key=lambda t: (t.pontos, t.vitorias, t.saldo_gols), reverse=True)[:6]

    # 2. Artilharia (Top 5 conforme o layout da imagem)
    artilheiros = Jogador.objects.all().order_by('-gols')[:5]
    
    # 3. Configurações Globais (Live Streaming e Título)
    config, created = ConfiguracaoGeral.objects.get_or_create(pk=1)

    # 4. Galeria de Fotos / Integração Instagram (RF04)
    # Pegamos as 9 fotos mais recentes para o grid 3x3 do layout
    fotos_galeria = FotoGaleria.objects.all().order_by('ordem', '-id')[:9]
    
    return render(request, 'torneio/index.html', {
        'times': times,
        'artilheiros': artilheiros,
        'config': config,
        'fotos_galeria': fotos_galeria,
    })

def tabela_classificacao(request):
    """
    Página exclusiva da Tabela (Menu: TABELA).
    """
    times = Time.objects.all()
    times = sorted(times, key=lambda t: (t.pontos, t.vitorias, t.saldo_gols), reverse=True)
    return render(request, 'torneio/tabela.html', {'times': times})

def lista_jogos(request):
    """
    Nova página exclusiva para o Calendário de Jogos (Menu: JOGOS).
    Separa os jogos por 'Próximos' e 'Resultados'.
    """
    agora = timezone.now()
    
    # Próximos Jogos (Ainda não finalizados ou data futura)
    proximos_jogos = Partida.objects.filter(finalizada=False).order_by('data_partida')
    
    # Resultados (Jogos já encerrados)
    resultados = Partida.objects.filter(finalizada=True).order_by('-data_partida')
    
    return render(request, 'torneio/jogos.html', {
        'proximos_jogos': proximos_jogos,
        'resultados': resultados
    })

def artilharia_completa(request):
    """
    Página detalhada de artilharia (Menu: ARTILHARIA).
    """
    artilheiros = Jogador.objects.all().order_by('-gols')
    return render(request, 'torneio/artilharia.html', {'artilheiros': artilheiros})

def artilharia_completa(request):
    # Busca todos os jogadores com gols > 0, ordenados do maior para o menor
    todos_artilheiros = Jogador.objects.filter(gols__gt=0).order_by('-gols')
    return render(request, 'torneio/artilharia.html', {'artilheiros': todos_artilheiros})