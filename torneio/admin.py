from django.contrib import admin
from .models import Time, Jogador, Partida, ConfiguracaoGeral, FotoGaleria

@admin.register(ConfiguracaoGeral)
class ConfiguracaoGeralAdmin(admin.ModelAdmin):
    # Adicionei 'proxima_live' aqui para você ver direto na tabela do Admin
    list_display = ('titulo_torneio', 'esta_ao_vivo', 'proxima_live', 'youtube_live_id')
    
    # Trava de Segurança: impede a criação de mais de um registro de configuração
    def has_add_permission(self, request):
        if ConfiguracaoGeral.objects.exists():
            return False
        return True

    # Impede a deleção da configuração para não quebrar o site
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('time_casa', 'gols_casa', 'gols_fora', 'time_fora', 'data_partida', 'finalizada')
    list_filter = ('data_partida', 'time_casa', 'time_fora', 'finalizada')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.time_casa.atualizar_estatisticas()
        obj.time_fora.atualizar_estatisticas()

    def delete_model(self, request, obj):
        casa = obj.time_casa
        fora = obj.time_fora
        super().delete_model(request, obj)
        casa.atualizar_estatisticas()
        fora.atualizar_estatisticas()

    def delete_queryset(self, request, queryset):
        times_para_atualizar = set()
        for partida in queryset:
            times_para_atualizar.add(partida.time_casa)
            times_para_atualizar.add(partida.time_fora)
        
        queryset.delete()
        
        for time in times_para_atualizar:
            time.atualizar_estatisticas()

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'vitorias', 'empates', 'derrotas', 'pontos')
    # Campos calculados via property/method devem ser readonly no admin
    readonly_fields = ('vitorias', 'empates', 'derrotas', 'gols_pro', 'gols_contra')

@admin.register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'time', 'gols', 'cartoes_amarelos', 'cartoes_vermelhos')
    list_filter = ('time',)
    search_fields = ('nome',)

@admin.register(FotoGaleria)
class FotoGaleriaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'ordem')
    list_editable = ('ordem',) # Permite mudar a ordem direto na lista