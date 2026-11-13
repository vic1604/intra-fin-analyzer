"""Contrato de dados (Pydantic v2).

Princípios:
  1. Todo número extraído carrega `Evidencia` (documento, página, trecho).
  2. Ausência é um estado explícito (`nao_encontrado`) — nunca zero, nunca
     estimativa.
  3. Valores CALCULADOS pelo pipeline (derivados) ficam separados dos valores
     EXTRAÍDOS do documento e sempre listam as entradas usadas.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Escala = Literal["unidade", "mil", "milhoes", "bilhoes"]
Unidade = Literal["R$", "%", "x"]
Status = Literal["encontrado", "nao_encontrado", "nao_verificado"]
Severidade = Literal["alta", "media", "baixa", "info"]


class Evidencia(BaseModel):
    documento: str
    pagina: int = Field(ge=1, description="posição física da página no PDF (1 = capa)")
    trecho: str = Field(min_length=3, description="trecho literal da página que contém o valor")
    verificada: bool | None = Field(default=None, description="preenchido pelo grounding")
    motivo_falha: str | None = None


class Valor(BaseModel):
    valor: float
    escala: Escala = "mil"
    unidade: Unidade = "R$"
    rotulo: str | None = None
    evidencia: Evidencia


class Metrica(BaseModel):
    status: Status = "encontrado"
    atual: Valor | None = None
    anterior: Valor | None = None
    variacao_reportada_pct: Valor | None = None
    variacao_reportada_abs: Valor | None = None
    alternativas: list[Valor] = Field(
        default_factory=list,
        description="outras menções do MESMO número no documento (ex.: texto da administração vs DFs)",
    )
    complementares: list[Valor] = Field(
        default_factory=list,
        description="números extras com evidência (ex.: componentes de capex, lucro atribuível a controladores); "
        "não são comparados com `atual`",
    )
    observacao: str | None = None
    motivo_ausencia: str | None = None
    termos_verificados: list[str] = Field(
        default_factory=list,
        description="para status=nao_encontrado: termos buscados no PDF inteiro cuja ausência é re-verificada por código",
    )


class AnomaliaDocumento(BaseModel):
    """Inconsistência/erro/ressalva encontrada NO PRÓPRIO documento (typos de
    período, números trocados, comparativo não auditado...)."""

    id: str
    severidade: Severidade
    descricao: str
    evidencias: list[Evidencia]


class Extracao(BaseModel):
    doc_id: str
    empresa: str
    periodo_referencia: str
    tipo_documento: str
    moeda_escala_declarada: str
    receita_liquida: Metrica
    receita_liquida_ex_construcao: Metrica | None = None
    receita_construcao: Metrica | None = None
    ebitda: Metrica
    margem_ebitda: Metrica
    lucro_liquido: Metrica
    divida_liquida: Metrica
    alavancagem: Metrica
    fco: Metrica
    capex: Metrica
    # insumos para cálculos derivados (também com evidência)
    ebit: Metrica
    depreciacao_amortizacao: Metrica
    caixa_equivalentes: Metrica
    aplicacoes_financeiras: Metrica
    divida_bruta: Metrica
    anomalias_documento: list[AnomaliaDocumento] = Field(default_factory=list)
    modo: str = "reference"  # reference | llm | baseline

    def metricas(self) -> dict[str, Metrica]:
        out = {}
        for nome in (
            "receita_liquida",
            "receita_liquida_ex_construcao",
            "receita_construcao",
            "ebitda",
            "margem_ebitda",
            "lucro_liquido",
            "divida_liquida",
            "alavancagem",
            "fco",
            "capex",
            "ebit",
            "depreciacao_amortizacao",
            "caixa_equivalentes",
            "aplicacoes_financeiras",
            "divida_bruta",
        ):
            m = getattr(self, nome)
            if m is not None:
                out[nome] = m
        return out


CAMPOS_ENTREGA = [
    "receita_liquida",
    "ebitda",
    "margem_ebitda",
    "lucro_liquido",
    "divida_liquida",
    "alavancagem",
    "fco",
    "capex",
]


# ----------------------------------------------------------- qualitativo ---

Tom = Literal["positivo", "neutro", "negativo"]

CATEGORIAS_RISCO = {
    "credito_inadimplencia": "Crédito / inadimplência de clientes",
    "juros_mercado": "Juros e risco de mercado",
    "liquidez_endividamento": "Liquidez e endividamento",
    "custo_insumos": "Custo de insumos / matérias-primas",
    "regulatorio_concessao": "Regulatório / fiscal / concessão",
    "contingencias_judiciais": "Contingências judiciais e tributárias",
    "continuidade_operacional": "Continuidade operacional",
    "concentracao_dependencia": "Concentração / dependência de contratos ou investida",
    "qualidade_informacao": "Qualidade / auditoria da informação",
}


class Item(BaseModel):
    texto: str
    evidencias: list[Evidencia]
    categoria: str | None = None  # só para riscos (taxonomia CATEGORIAS_RISCO)


class Qualitativo(BaseModel):
    doc_id: str
    empresa: str
    fonte_qualitativa: str = Field(description="de onde vem a análise: relatório da administração ou apenas notas explicativas")
    nota_cobertura: str = ""
    motivos_resultado: list[Item]
    motivo_variacao_receita: Item | None = None
    riscos: list[Item]
    guidance: list[Item] = Field(default_factory=list)
    guidance_numerico_encontrado: bool = False
    eventos_relevantes: list[Item]
    tom: Tom
    tom_justificativa: str
    tom_evidencias: list[Evidencia]
    confianca_tom: Literal["alta", "media", "baixa"] = "media"
    modo: str = "reference"
