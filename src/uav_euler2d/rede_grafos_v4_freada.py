# -*- coding: utf-8 -*-
"""
Rede em grafos, versão 4: a rede "freada" (contra o sobreajuste).

Igual à versão 3 (mesma validação cruzada, mesmo Kriging nas mesmas partes,
mesma reprodutibilidade), com duas mudanças, ambas contra o sobreajuste
observado na versão 3 (erro no treino 10 a 50 vezes menor que na validação):

  (a) rede menor: OCULTO = 32 em vez de 64 (cerca de 4 vezes menos pesos);
  (b) penalização de pesos grandes com o otimizador AdamW
      (Loshchilov & Hutter, "Decoupled Weight Decay Regularization",
      ICLR 2019), com PESO_DECAIMENTO = 0,01 (o valor padrão do PyTorch).

Os resultados de cada parte são gravados em resultados_cv_<NOME>.csv, para
comparar versões depois.

Histórico da versão 3:

O que muda em relação à versão 2:

1. VALIDAÇÃO CRUZADA (k partes, por geometria).  Os perfis de treino e de
   validação (46) são juntados e divididos em K partes.  O modelo é treinado
   K vezes; em cada vez, uma parte fica de fora e serve de validação, e as
   outras servem de treino.  Assim, todos os 46 perfis são usados como
   validação exatamente uma vez, e a nota fica bem mais estável do que com
   um grupo fixo de 8 perfis (Hastie, Tibshirani & Friedman, The Elements of
   Statistical Learning, cap. 7).  O grupo de TESTE não é usado.

2. O KRIGING É AVALIADO NAS MESMAS PARTES.  A comparação é "pareada": rede e
   Kriging são treinados e validados exatamente nos mesmos perfis, e a
   diferença entre os dois é calculada parte a parte.

3. RESULTADOS REPRODUZÍVEIS.  Com DETERMINISTICO = True, o PyTorch usa só
   algoritmos determinísticos e um único núcleo, e o mesmo código dá sempre
   o mesmo número (o treino fica mais lento).

4. A NORMALIZAÇÃO usa só os perfis de treino de cada parte (para a
   validação nunca "vazar" para o treino).

Uso:  python rede_grafos_v4_freada.py
"""

import copy
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel, RBF, WhiteKernel
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch_geometric.nn import GINEConv, global_mean_pool

# ======================================================================
# 0. CONFIGURAÇÃO
# ======================================================================
pasta = Path(r'C:\Users\jpvas\AEROFOLIO\dataset_euler_2d\dataset_euler_2d_banco_v2\dataset_euler_2d')
if len(sys.argv) > 1:
    pasta = Path(sys.argv[1])
ALPHA = math.radians(2.0)
CORDA = 1.0
OCULTO = 32                   # v4: era 64
CAMADAS = 6
EPOCAS = 1500
TAXA = 1e-3
TAXA_FINAL = 1e-5
PESO_DECAIMENTO = 0.01         # v4: penalização dos pesos (AdamW)
NOME = 'v4_freada'            # nome do experimento, usado no arquivo de resultados
LOTE = 8
K_PARTES = 5                  # número de partes da validação cruzada
SEMENTE = 42
DETERMINISTICO = True         # True: sempre o mesmo resultado (mais lento)

if DETERMINISTICO:
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(1)


def fixar_semente(semente):
    random.seed(semente); np.random.seed(semente); torch.manual_seed(semente)


# ======================================================================
# 1. MONTAR O GRAFO DE UM CASO (igual à versão 2)
# ======================================================================
def montar_grafo(case_id, CL, CD):
    s = pd.read_parquet(pasta / 'surface' / f'case_{case_id}.parquet').sort_values('contour_index')
    n = len(s)
    x = np.column_stack([s['x_over_c'], s['y_over_c'], s['s_over_c'],
                         s['normal_x'], s['normal_y'], s['segment_length_m'] / CORDA,
                         (s['side'] == 'upper').astype(float)])
    origem = np.arange(n)
    destino = (origem + 1) % n
    de = np.concatenate([origem, destino])
    pra = np.concatenate([destino, origem])
    xy = s[['x_over_c', 'y_over_c']].values
    nrm = s[['normal_x', 'normal_y']].values
    d = xy[pra] - xy[de]
    comp = np.linalg.norm(d, axis=1)
    escalar = (nrm[de] * nrm[pra]).sum(axis=1)
    bivetor = nrm[de, 0] * nrm[pra, 1] - nrm[de, 1] * nrm[pra, 0]
    atributos = np.column_stack([d[:, 0], d[:, 1], comp, escalar, bivetor])
    t = lambda a, tipo=torch.float32: torch.tensor(a, dtype=tipo)
    return Data(x=t(x), edge_index=t(np.vstack([de, pra]), torch.long), edge_attr=t(atributos),
                y=t(s['Cp'].values.reshape(-1, 1)), normal=t(nrm), ds=t(s['segment_length_m'].values),
                CL=t([CL]), CD=t([CD]), case_id=case_id)


# ======================================================================
# 2. LER OS CASOS E MONTAR AS K PARTES (só treino + validação)
# ======================================================================
casos = pd.read_csv(pasta / 'cases.csv')
casos = casos[casos['status'].isin(['success', 'non_converged'])]
split = json.load(open(pasta / 'split_manifest.json'))
disponiveis = casos[casos['geometry_id'].isin(split['train'] + split['val'])].reset_index(drop=True)

grafos = {r.case_id: montar_grafo(r.case_id, r.CL, r.CD) for r in disponiveis.itertuples()}

geometrias = sorted(disponiveis['geometry_id'].unique())
ordem = np.random.default_rng(SEMENTE).permutation(len(geometrias))
partes = [sorted(geometrias[i] for i in ordem[k::K_PARTES]) for k in range(K_PARTES)]
print(f'{len(disponiveis)} perfis em {K_PARTES} partes:', [len(p) for p in partes])


# ======================================================================
# 3. A REDE (igual à versão 2)
# ======================================================================
def mlp(entra, sai):
    return nn.Sequential(nn.Linear(entra, OCULTO), nn.SiLU(), nn.Linear(OCULTO, sai))

class RedeGrafos(nn.Module):
    def __init__(self):
        super().__init__()
        self.codifica_no = mlp(7, OCULTO)
        self.codifica_aresta = mlp(5, OCULTO)
        self.vizinhos = nn.ModuleList([GINEConv(mlp(OCULTO, OCULTO), edge_dim=OCULTO) for _ in range(CAMADAS)])
        self.global_ = nn.ModuleList([mlp(2 * OCULTO, OCULTO) for _ in range(CAMADAS)])
        self.normas = nn.ModuleList([nn.LayerNorm(OCULTO) for _ in range(CAMADAS)])
        self.decodifica = mlp(OCULTO, 1)

    def forward(self, g):
        h = self.codifica_no(g.x)
        e = self.codifica_aresta(g.edge_attr)
        for viz, glo, norma in zip(self.vizinhos, self.global_, self.normas):
            m = viz(h, g.edge_index, e)
            resumo = global_mean_pool(m, g.batch)[g.batch]
            h = norma(h + glo(torch.cat([m, resumo], dim=1)))
        return self.decodifica(h)


# ======================================================================
# 4. NORMALIZAÇÃO, TREINO E AVALIAÇÃO DE UMA PARTE
# ======================================================================
def normalizar(lista_treino, lista_valid):
    """Estatísticas só do treino desta parte; devolve cópias normalizadas."""
    X = torch.cat([g.x for g in lista_treino]); A = torch.cat([g.edge_attr for g in lista_treino])
    Y = torch.cat([g.y for g in lista_treino])
    mx, sx = X.mean(0), X.std(0).clamp_min(1e-8); mx[-1], sx[-1] = 0.0, 1.0
    ma, sa = A.mean(0), A.std(0).clamp_min(1e-8)
    my, sy = Y.mean(), Y.std()
    def copia(g):
        h = copy.copy(g)
        h.x = (g.x - mx) / sx; h.edge_attr = (g.edge_attr - ma) / sa; h.y_norm = (g.y - my) / sy
        return h
    return [copia(g) for g in lista_treino], [copia(g) for g in lista_valid], (my, sy)


def treinar(lista_treino, lista_valid):
    fixar_semente(SEMENTE)
    rede = RedeGrafos()
    otimizador = torch.optim.AdamW(rede.parameters(), lr=TAXA, weight_decay=PESO_DECAIMENTO)
    agenda = torch.optim.lr_scheduler.CosineAnnealingLR(otimizador, T_max=EPOCAS, eta_min=TAXA_FINAL)
    gerador = torch.Generator().manual_seed(SEMENTE)
    carregador = DataLoader(lista_treino, batch_size=LOTE, shuffle=True, generator=gerador)
    lote_valid = next(iter(DataLoader(lista_valid, batch_size=len(lista_valid))))
    perda_fn = nn.MSELoss()
    melhor, melhor_estado = float('inf'), None
    for epoca in range(1, EPOCAS + 1):
        rede.train()
        for lote in carregador:
            otimizador.zero_grad()
            perda = perda_fn(rede(lote), lote.y_norm)
            perda.backward()
            otimizador.step()
        agenda.step()
        rede.eval()
        with torch.no_grad():
            perda_val = perda_fn(rede(lote_valid), lote_valid.y_norm).item()
        if perda_val < melhor:
            melhor, melhor_estado = perda_val, {k: v.clone() for k, v in rede.state_dict().items()}
        if epoca % 250 == 0:
            print(f'    época {epoca:5d} | erro no treino {perda.item():.5f} | erro na validação {perda_val:.5f}')
    rede.load_state_dict(melhor_estado)
    return rede


def integrar(cp, g):
    cf = -(cp[:, None] * g.normal * g.ds[:, None]).sum(0) / CORDA
    return ((-cf[0] * math.sin(ALPHA) + cf[1] * math.cos(ALPHA)).item(),
            (cf[0] * math.cos(ALPHA) + cf[1] * math.sin(ALPHA)).item())


def avaliar_rede(rede, lista_valid, my, sy):
    rede.eval(); erros_cp, cl, cd, cl_real, cd_real = [], [], [], [], []
    with torch.no_grad():
        for g in lista_valid:
            cp = (rede(next(iter(DataLoader([g], batch_size=1)))) * sy + my)[:, 0]
            erros_cp.append(torch.sqrt(((cp - g.y[:, 0]) ** 2).mean()).item())
            a, b = integrar(cp, g); cl.append(a); cd.append(b)
            cl_real.append(g.CL.item()); cd_real.append(g.CD.item())
    return metricas(np.array(cl), np.array(cl_real), np.array(cd), np.array(cd_real), np.mean(erros_cp))


def avaliar_kriging(tab_treino, tab_valid):
    li, ls = np.array([0.00, 0.20, 0.08]), np.array([0.04, 0.60, 0.16])
    Xt = (tab_treino[['m', 'p', 't']].values - li) / (ls - li)
    Xv = (tab_valid[['m', 'p', 't']].values - li) / (ls - li)
    prev = {}
    for col in ['CL', 'CD']:
        gp = GaussianProcessRegressor(ConstantKernel(1.0) * RBF([0.5, 0.5, 0.5]) + WhiteKernel(1e-3),
                                      normalize_y=True, n_restarts_optimizer=10, random_state=SEMENTE)
        prev[col] = gp.fit(Xt, tab_treino[col].values).predict(Xv)
    return metricas(prev['CL'], tab_valid['CL'].values, prev['CD'], tab_valid['CD'].values, np.nan)


def metricas(cl, cl_real, cd, cd_real, erro_cp):
    rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))
    return {'Cp': erro_cp,
            'CL': rmse(cl, cl_real), 'CL_%': 100 * rmse(cl, cl_real) / cl_real.mean(),
            'CD': rmse(cd, cd_real), 'CD_%': 100 * rmse(cd, cd_real) / cd_real.mean()}


# ======================================================================
# 5. A VALIDAÇÃO CRUZADA
# ======================================================================
print(f'experimento {NOME}: OCULTO={OCULTO}, CAMADAS={CAMADAS}, weight_decay={PESO_DECAIMENTO}, '
      f'{sum(p.numel() for p in RedeGrafos().parameters())} pesos ajustáveis')
res_rede, res_krig = [], []
for k, parte in enumerate(partes, start=1):
    tab_valid = disponiveis[disponiveis['geometry_id'].isin(parte)]
    tab_treino = disponiveis[~disponiveis['geometry_id'].isin(parte)]
    print(f'\n### parte {k}/{K_PARTES}: treino {len(tab_treino)} perfis | validação {len(tab_valid)} perfis')
    tr, va, (my, sy) = normalizar([grafos[c] for c in tab_treino.case_id], [grafos[c] for c in tab_valid.case_id])
    rede = treinar(tr, va)
    r, q = avaliar_rede(rede, va, my, sy), avaliar_kriging(tab_treino, tab_valid)
    res_rede.append(r); res_krig.append(q)
    print(f'  rede   : Cp {r["Cp"]:.4f} | CL {r["CL"]:.4f} ({r["CL_%"]:.1f}%) | CD {r["CD"]:.5f} ({r["CD_%"]:.1f}%)')
    print(f'  Kriging:             CL {q["CL"]:.4f} ({q["CL_%"]:.1f}%) | CD {q["CD"]:.5f} ({q["CD_%"]:.1f}%)')
    torch.save(rede.state_dict(), f'rede_cv_parte{k}.pt')

R, Q = pd.DataFrame(res_rede), pd.DataFrame(res_krig)
print(f'\n===== VALIDAÇÃO CRUZADA ({K_PARTES} partes): média ± desvio entre as partes =====')
print(f'Rede   : Cp {R.Cp.mean():.4f} ± {R.Cp.std():.4f} | '
      f'CL {R.CL.mean():.4f} ± {R.CL.std():.4f} ({R["CL_%"].mean():.1f}%) | '
      f'CD {R.CD.mean():.5f} ± {R.CD.std():.5f} ({R["CD_%"].mean():.1f}%)')
print(f'Kriging:                     '
      f'CL {Q.CL.mean():.4f} ± {Q.CL.std():.4f} ({Q["CL_%"].mean():.1f}%) | '
      f'CD {Q.CD.mean():.5f} ± {Q.CD.std():.5f} ({Q["CD_%"].mean():.1f}%)')
dif_cl, dif_cd = R.CL - Q.CL, R.CD - Q.CD
pd.concat([R.add_prefix('rede_'), Q.drop(columns='Cp').add_prefix('kriging_')], axis=1).rename_axis('parte').to_csv(
    f'resultados_cv_{NOME}.csv')
print(f'Diferença rede − Kriging, parte a parte: CL {dif_cl.mean():+.4f} ± {dif_cl.std():.4f} | '
      f'CD {dif_cd.mean():+.5f} ± {dif_cd.std():.5f}')
print('(diferença negativa = a rede errou menos; se o ± for maior que a média, é empate)')
