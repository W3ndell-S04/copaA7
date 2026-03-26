from django.contrib import admin
from .models import Time, Jogador, Partida

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('time_casa', 'gols_casa', 'gols_fora', 'time_fora', 'data_partida')
    
    # 1. Garante o recálculo ao salvar pelo Admin
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.time_casa.atualizar_estatisticas()
        obj.time_fora.atualizar_estatisticas()

    # 2. Garante o recálculo ao apagar UMA partida individualmente
    def delete_model(self, request, obj):
        casa = obj.time_casa
        fora = obj.time_fora
        super().delete_model(request, obj)
        casa.atualizar_estatisticas()
        fora.atualizar_estatisticas()

    # 3. SOLUÇÃO DO BUG CRÍTICO: Garante o recálculo ao apagar várias partidas de uma vez
    def delete_queryset(self, request, queryset):
        # Criamos um set para não repetir o recálculo do mesmo time várias vezes
        times_para_atualizar = set()
        for partida in queryset:
            times_para_atualizar.add(partida.time_casa)
            times_para_atualizar.add(partida.time_fora)
        
        # Deleta as partidas selecionadas
        queryset.delete()
        
        # Recalcula cada time envolvido após a deleção em massa
        for time in times_para_atualizar:
            time.atualizar_estatisticas()

# Registros simples para os outros modelos
admin.site.register(Time)
admin.site.register(Jogador)