from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

class Time(models.Model):
    nome = models.CharField(max_length=100)
    escudo = models.URLField(max_length=500, null=True, blank=True)
    
    # Estatísticas (campos brutos persistidos no banco)
    vitorias = models.PositiveIntegerField(default=0)
    empates = models.PositiveIntegerField(default=0)
    derrotas = models.PositiveIntegerField(default=0)
    gols_pro = models.PositiveIntegerField(default=0)
    gols_contra = models.PositiveIntegerField(default=0)

    @property
    def pontos(self):
        return (self.vitorias * 3) + self.empates

    @property
    def saldo_gols(self):
        return self.gols_pro - self.gols_contra

    def __str__(self):
        return self.nome

    def atualizar_estatisticas(self):
        """
        Lógica Centralizada: Percorre todas as partidas do time 
        (casa ou fora) e reconstrói os números do zero.
        """
        v = e = d = gp = gc = 0
        
        # Filtra todas as partidas onde este time participou
        # Importamos Partida localmente para evitar importação circular
        from .models import Partida
        jogos = Partida.objects.filter(Q(time_casa=self) | Q(time_fora=self))

        for p in jogos:
            if p.time_casa == self:
                gp += p.gols_casa
                gc += p.gols_fora
                if p.gols_casa > p.gols_fora: v += 1
                elif p.gols_casa < p.gols_fora: d += 1
                else: e += 1
            else:
                gp += p.gols_fora
                gc += p.gols_casa
                if p.gols_fora > p.gols_casa: v += 1
                elif p.gols_fora < p.gols_casa: d += 1
                else: e += 1
        
        # Atualiza os campos e salva os novos valores recalculados
        self.vitorias = v
        self.empates = e
        self.derrotas = d
        self.gols_pro = gp
        self.gols_contra = gc
        self.save()

    def resetar_estatisticas(self):
        """Zera manualmente os dados do time"""
        self.vitorias = 0
        self.empates = 0
        self.derrotas = 0
        self.gols_pro = 0
        self.gols_contra = 0
        self.save()

class Jogador(models.Model):
    nome = models.CharField(max_length=100)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='jogadores')
    foto = models.URLField(max_length=500, null=True, blank=True)
    gols = models.PositiveIntegerField(default=0)
    cartoes_amarelos = models.PositiveIntegerField(default=0)
    cartoes_vermelhos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.nome

class Partida(models.Model):
    time_casa = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='jogos_casa')
    time_fora = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='jogos_fora')
    gols_casa = models.PositiveIntegerField(default=0)
    gols_fora = models.PositiveIntegerField(default=0)
    data_partida = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Trava de segurança: impede que um time jogue contra ele mesmo"""
        if self.time_casa == self.time_fora:
            raise ValidationError("Erro: O time da casa não pode ser o mesmo que o visitante.")

    def save(self, *args, **kwargs):
        # Força a validação do método clean()
        self.full_clean()
        super().save(*args, **kwargs)
        # Recalcula estatísticas para garantir integridade após salvar
        self.time_casa.atualizar_estatisticas()
        self.time_fora.atualizar_estatisticas()

    def delete(self, *args, **kwargs):
        # Guarda a referência antes de sumir com a partida
        casa = self.time_casa
        fora = self.time_fora
        super().delete(*args, **kwargs)
        # Recalcula os times agora que esta partida não existe mais no banco
        casa.atualizar_estatisticas()
        fora.atualizar_estatisticas()

    def __str__(self):
        return f"{self.time_casa} {self.gols_casa} x {self.gols_fora} {self.time_fora}"