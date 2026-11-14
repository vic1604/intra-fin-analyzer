# Conferência manual de valores (feita à mão, direto no PDF)

Além da verificação automática (`scripts/verify_numbers.py` confere cada trecho e número direto no PDF, sem usar o código do pipeline), conferi **8 valores** abrindo as páginas dos PDFs com `pdftotext -layout`. Resultado: **os 8 estavam corretos**. Duas particularidades dos próprios documentos ficaram documentadas:

1. **Light, EBITDA (p.9/p.20):** o texto da administração traz "+1.180" sem o sinal negativo; o EBITDA recomposto pela DRE é −1.179,6 (R$ mi). O pipeline mantém os dois e sinaliza a divergência (validação C04). Não corrige em silêncio.
2. **Millet, receita (p.29):** a Millet consolida a Alibra desde 18/06/2021, então o crescimento de +131,9% não é comparável (≈ +45% numa base comparável). Está sinalizado no relatório.

Outras checagens de consistência:
- **Light, dívida líquida:** R$ 9.032 mi aparece no texto da administração (p.10, junto ao múltiplo de covenants 3,32x) e na tabela de capital (p.105: 9.032.236 mil). Mesmo valor em duas páginas; as respostas citam a que sustenta cada afirmação.
- **Brasal:** caixa líquido (dívida líquida negativa de −171.605 mil), por isso não há múltiplo de alavancagem.

Reproduzir: `python scripts/verify_numbers.py` e `python -m finanalyzer eval --mode baseline`.
