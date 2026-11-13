"""Validação TOLERANTE da saída de LLMs.

Modelos reais (sobretudo no modo `json_object`, que não impõe o schema) erram
detalhes: omitem um campo obrigatório de UM item, devolvem string onde se
esperava objeto etc. Falhar o documento inteiro por causa disso desperdiça a
chamada (e o dinheiro/cota). Aqui, em vez de abortar:

  1. valida o JSON inteiro;
  2. se falhar, DESCARTA somente o item da lista que causou o erro (nunca
     "conserta" o conteúdo inventando valores) e valida de novo;
  3. registra um warning por item descartado e devolve a lista de avisos.

Itens descartados significam "não encontrado" — o mesmo caminho seguro do
grounding: na dúvida, a informação não entra no relatório.
Campos escalares inválidos de nível raiz são removidos (usam o default); se o
campo não tem default, o erro original é propagado.
"""

from __future__ import annotations

import copy
import logging
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

log = logging.getLogger("finanalyzer.lenient")
T = TypeVar("T", bound=BaseModel)
_MAX_PASSES = 500


def _resolve(data: Any, path: tuple) -> Any:
    cur = data
    for p in path:
        cur = cur[p]
    return cur


def _victim(loc: tuple) -> tuple[tuple, int | str] | None:
    """(caminho do contêiner, chave a remover) = item de lista MAIS INTERNO no erro;
    sem lista no caminho, o campo de nível raiz."""
    last_int = None
    for i, p in enumerate(loc):
        if isinstance(p, int):
            last_int = i
    if last_int is not None:
        return loc[:last_int], loc[last_int]
    return ((), loc[0]) if loc else None


def _unwrap_list(data: Any, avisos: list[str], what: str) -> Any:
    """Alguns modelos embrulham o objeto numa lista: [{...}]. Aceita se houver UM objeto
    (ou funde vários objetos, o primeiro valor de cada chave prevalece)."""
    if not isinstance(data, list):
        return data
    objs = [d for d in data if isinstance(d, dict)]
    if not objs:
        return data
    avisos.append(f"{what}: resposta veio como lista de {len(objs)} objeto(s); usando o conteúdo como objeto único")
    merged: dict = {}
    for o in objs:
        for k, v in o.items():
            if k not in merged:
                merged[k] = v
            elif isinstance(merged[k], list) and isinstance(v, list):
                merged[k] = merged[k] + v
    return merged


def lenient_validate(model: type[T], data: dict, what: str = "") -> tuple[T, list[str]]:
    avisos: list[str] = []
    data = _unwrap_list(copy.deepcopy(data), avisos, what or model.__name__)
    removidos: set[tuple] = set()
    for _ in range(_MAX_PASSES):
        try:
            return model.model_validate(data), avisos
        except ValidationError as e:
            alvos: dict[tuple, set] = {}
            for err in e.errors():
                v = _victim(tuple(err["loc"]))
                if v is None:
                    raise
                container, key = v
                try:
                    alvo = _resolve(data, container)
                except (KeyError, IndexError, TypeError):
                    raise e from None
                if isinstance(alvo, dict) and not isinstance(key, int):
                    if key not in alvo:  # campo obrigatório ausente no nível raiz: sem como seguir
                        raise
                if (container, key) in removidos and not isinstance(key, int):
                    raise  # remover não resolveu (campo obrigatório) — propaga o erro real
                alvos.setdefault(container, set()).add(key)
                avisos.append(f"{what or model.__name__}: descartado {'.'.join(map(str, container + (key,)))} — {err['msg']}")
            for container, keys in alvos.items():
                alvo = _resolve(data, container)
                if isinstance(alvo, list):
                    for k in sorted((k for k in keys if isinstance(k, int)), reverse=True):
                        if k < len(alvo):
                            alvo.pop(k)
                elif isinstance(alvo, dict):
                    for k in keys:
                        alvo.pop(k, None)
                        removidos.add((container, k))
    raise RuntimeError(f"validação tolerante não convergiu ({what or model.__name__})")  # pragma: no cover


def warn_all(avisos: list[str]) -> None:
    for a in avisos:
        log.warning(a)
