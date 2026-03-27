from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

class Time(models.Model):
    nome = models.CharField(max_length=100)
    escudo = models.URLField(max_length=500, null=True, blank=True)
    
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
        # Import local para evitar importação circular
        from .models import Partida
        v = e = d = gp = gc = 0
        # Apenas partidas finalizadas contam para a tabela
        jogos = Partida.objects.filter(Q(time_casa=self) | Q(time_fora=self), finalizada=True)

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
        
        self.vitorias = v
        self.empates = e
        self.derrotas = d
        self.gols_pro = gp
        self.gols_contra = gc
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
    # Alterado para permitir agendar jogos no futuro
    data_partida = models.DateTimeField(verbose_name="Data e Hora do Jogo")
    finalizada = models.BooleanField(default=False, verbose_name="Partida Encerrada?")

    class Meta:
        ordering = ['data_partida']
        verbose_name = "Partida"
        verbose_name_plural = "Partidas"

    def clean(self):
        if self.time_casa == self.time_fora:
            raise ValidationError("Erro: O time da casa não pode ser o mesmo que o visitante.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Atualiza a tabela sempre que uma partida é salva
        self.time_casa.atualizar_estatisticas()
        self.time_fora.atualizar_estatisticas()

    def delete(self, *args, **kwargs):
        casa = self.time_casa
        fora = self.time_fora
        super().delete(*args, **kwargs)
        casa.atualizar_estatisticas()
        fora.atualizar_estatisticas()

    def __str__(self):
        status = "[ENCERRADA]" if self.finalizada else "[AGENDADA]"
        return f"{status} {self.time_casa} {self.gols_casa} x {self.gols_fora} {self.time_fora}"

class ConfiguracaoGeral(models.Model):
    titulo_torneio = models.CharField(max_length=100, default="Copa Área 7")
    youtube_live_id = models.CharField(max_length=20, blank=True, help_text="ID do vídeo da LIVE")
    playlist_id = models.CharField(max_length=100, blank=True, help_text="ID da Playlist")
    esta_ao_vivo = models.BooleanField(default=False)
    proxima_live = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Configuração Geral"
        verbose_name_plural = "Configuração Geral"

    def __str__(self):
        return self.titulo_torneio

class FotoGaleria(models.Model):
    titulo = models.CharField(max_length=100, blank=True, verbose_name="Título/Legenda")
    imagem_url = models.URLField(max_length=500)
    link_post = models.URLField(max_length=500, blank=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Foto da Galeria"
        verbose_name_plural = "Galeria de Fotos"
        ordering = ['ordem', '-id']

    def __str__(self):
        return self.titulo or f"Foto {self.id}"